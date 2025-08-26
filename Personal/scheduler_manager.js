const { Client } = require('pg');
const { CloudTasksClient } = require('@google-cloud/tasks');
const functions = require('@google-cloud/functions-framework');


const tasksClient = new CloudTasksClient();

const PROJECT_ID = 'deploy-461918';
const LOCATION = 'southamerica-east1'; 
const QUEUE_NAME = 'tagfy-queue';

function getDbConnection() {
    return new Client({
        connectionString: "postgresql://neondb_owner:npg_MQphA3BFf0gP@ep-wispy-bonus-acat1phz-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    });
}

async function getProductsToMine() {
    const client = getDbConnection();
    
    try {
        await client.connect();
        
        const query = `
            SELECT id, user_id, url, store, price, last_mined_at, next_mine_at
            FROM monitors 
            WHERE next_mine_at <= CURRENT_TIMESTAMP
            ORDER BY next_mine_at ASC
        `;
        
        const result = await client.query(query);
        
        const products = result.rows.map(row => ({
            id: row.id,
            user_id: row.user_id,
            url: row.url,
            store: row.store,
            current_price: row.price,
            last_mined_at: row.last_mined_at ? row.last_mined_at.toISOString() : null,
            next_mine_at: row.next_mine_at ? row.next_mine_at.toISOString() : null
        }));
        
        return products;
        
    } catch (error) {
        console.error('Erro ao buscar produtos:', error);
        return [];
    } finally {
        await client.end();
    }
}

async function addTaskToQueue(store, url, productId, userId) {
    try {
        const parent = tasksClient.queuePath(PROJECT_ID, LOCATION, QUEUE_NAME);
        
        const scraperUrls = {
            'amazon': 'https://tagfy-amazon-575184900812.southamerica-east1.run.app',
            'aliexpress': 'https://tagfy-aliexpress-575184900812.southamerica-east1.run.app',
            'mercadolivre': 'https://tagfy-mercadolivre-575184900812.southamerica-east1.run.app',
            'magalu': 'https://tagfy-magalu-575184900812.southamerica-east1.run.app',
            'fastshop': 'https://tagfy-fastshop-575184900812.southamerica-east1.run.app',
            'americanas': 'https://tagfy-americanas-575184900812.southamerica-east1.run.app',
            'cea': 'https://tagfy-cea-575184900812.southamerica-east1.run.app'
        };
        
        if (!scraperUrls[store]) {
            throw new Error(`Loja não suportada: ${store}`);
        }
        
        const payload = {
            url: url,
            product_id: productId,
            userId: userId,
            store: store
        };
        
        const task = {
            httpRequest: {
                httpMethod: 'POST',
                url: scraperUrls[store],
                headers: {
                    'Content-Type': 'application/json',
                },
                body: Buffer.from(JSON.stringify(payload)).toString('base64'),
            },
            scheduleTime: {
                seconds: Math.floor(Date.now() / 1000) + 10,
            },
        };
        
        const [response] = await tasksClient.createTask({
            parent: parent,
            task: task,
        });
        
        console.log(`Tarefa criada: ${response.name}`);
        return {
            success: true,
            taskName: response.name,
            store: store,
            url: url,
            userId: userId
        };
        
    } catch (error) {
        console.error(`Erro ao criar tarefa para ${store}:`, error);
        return {
            success: false,
            error: error.message,
            store: store,
            url: url,
            userId: userId
        };
    }
}

functions.http('schedulerManager', async (req, res) => {
    try {
        console.log('Iniciando scheduler manager...');
        
        const productsToMine = await getProductsToMine();
        
        if (productsToMine.length === 0) {
            return res.json({
                message: 'Nenhum produto precisa ser atualizado no momento',
                products_checked: 0,
                timestamp: new Date().toISOString()
            });
        }
        
        console.log(`Encontrados ${productsToMine.length} produtos para minerar`);
        
        const results = [];
        let successCount = 0;
        let errorCount = 0;
        
        for (const product of productsToMine) {
            console.log(`Adicionando na fila: ${product.store} - ${product.url.substring(0, 50)}...`);
            
            const taskResult = await addTaskToQueue(product.store, product.url, product.id, product.user_id);
            
            const result = {
                product_id: product.id,
                user_id: product.user_id,
                store: product.store,
                url: product.url,
                previous_price: product.current_price,
                task_result: taskResult
            };
            
            if (taskResult.success) {
                successCount++;
                result.status = 'queued';
                result.task_name = taskResult.taskName;
            } else {
                errorCount++;
                result.status = 'error';
                result.error = taskResult.error;
            }
            
            results.push(result);
        }
        
        res.json({
            message: 'Processamento concluído',
            total_products: productsToMine.length,
            queued_count: successCount,
            error_count: errorCount,
            results: results,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Erro no scheduler manager:', error);
        res.status(500).json({
            error: 'Erro interno do servidor',
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});
