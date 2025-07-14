using System;
using Searchly;

namespace Searchly 
{

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== BEM-VINDO AO GERENCIADOR DE TAREFAS COM PERSISTÊNCIA HÍBRIDA ===\n");

            TaskManager taskManager = new TaskManager();

            // ===== Adicionando Tarefas =====
            Console.WriteLine("=== ADICIONANDO TAREFAS ===\n");
            
            Task task1 = new Task(
                "Estudar C# e POO",
                "Revisar os conceitos de classes, objetos, herança, polimorfismo, encapsulamento e abstração. Focar especialmente em interfaces e classes abstratas.",
                "Médio",
                DateTime.Now,
                DateTime.Now.AddDays(10)
            );

            Task task2 = new Task(
                "Fazer compras",
                "Comprar leite, pão, ovos, frutas, verduras, carne e produtos de limpeza para a semana",
                "Baixa",
                DateTime.Now,
                DateTime.Now.AddDays(2)
            );
            
            Task task3 = new Task(
                "Ir na academia",
                "Fazer 1 hora de musculação focando em pernas e glúteos. Incluir exercícios de cardio por 20 minutos",
                "Média",
                DateTime.Now,
                DateTime.Now.AddDays(1)
            );

            Task task4 = new Task(
                "Reunião com Juju",
                "Reunião com Juju para discutir sobre API e arquitetura do sistema. Preparar apresentação dos pontos principais",
                "Alta",
                DateTime.Now,
                DateTime.Now.AddDays(7)
            );

            Task task5 = new Task(
                "Organizar agenda pois Juju vai pedir",
                "Organizar minha agenda com meus horários ONLINE!!! Incluir reuniões, compromissos e tempo para desenvolvimento",
                "Baixa",
                DateTime.Now,
                DateTime.Now.AddDays(3)
            );

            taskManager.AddTask(task1);
            taskManager.AddTask(task2);
            taskManager.AddTask(task3);
            taskManager.AddTask(task4);
            taskManager.AddTask(task5);

            // ===== Listando Todas as Tarefas =====
            taskManager.ListAllTasks();

            // ===== Estatísticas Iniciais =====
            taskManager.ShowStatistics();

            // ===== Concluindo Algumas Tarefas =====
            Console.WriteLine("\n=== CONCLUINDO TAREFAS ===\n");
            taskManager.CompleteTaskByName("Fazer compras");
            taskManager.CompleteTaskByName("Ir na academia");

            // ===== Listando Tarefas Pendentes =====
            taskManager.ListPendingTasks();

            // ===== Listando Tarefas Concluídas =====
            taskManager.ListCompletedTasks();

            // ===== Estatísticas Após Conclusões =====
            taskManager.ShowStatistics();

            // ===== Buscando Tarefas =====
            Console.WriteLine("\n=== BUSCANDO TAREFAS ===\n");
            var tarefaEncontrada = taskManager.FindTaskByName("Estudar C# e POO");
            if (tarefaEncontrada != null)
            {
                Console.WriteLine("Tarefa encontrada:");
                Console.WriteLine(tarefaEncontrada.ToString());
            }
            else
            {
                Console.WriteLine("Tarefa não encontrada.");
            }

            // ===== Removendo Tarefa =====
            Console.WriteLine("\n=== REMOVENDO TAREFA ===\n");
            taskManager.RemoveTaskByName("Reunião com Juju");
            taskManager.ListAllTasks();

            // ===== Tentando Remover Tarefa Inexistente =====
            taskManager.RemoveTaskByName("Tarefa inexistente");

            // ===== Tentando Concluir Tarefa Inexistente =====
            taskManager.CompleteTaskByName("Tarefa que não existe");

            // ===== Estatísticas Finais =====
            taskManager.ShowStatistics();

            // ===== Métodos Utilitários =====
            Console.WriteLine($"\nTotal de tarefas: {taskManager.GetTaskCount()}");
            Console.WriteLine($"Existem tarefas? {taskManager.HasTasks()}");

            // ===== Concluindo Tarefa Restante =====
            taskManager.CompleteTaskByName("Estudar C# e POO");
            taskManager.ListAllTasks();
            taskManager.ShowStatistics();

            // ===== Listando Tarefas Pendentes (Vazio) =====
            taskManager.ListPendingTasks();

            // ===== Listando Tarefas Concluídas (Todas) =====
            taskManager.ListCompletedTasks();

            // ===== Demonstração da Persistência =====
            Console.WriteLine("\n=== DEMONSTRAÇÃO DA PERSISTÊNCIA HÍBRIDA ===\n");
            
            Console.WriteLine("Salvando todas as tarefas na persistência...");
            taskManager.SaveAllTasks();
            
            Console.WriteLine("\nCriando novo gerenciador para demonstrar carregamento...");
            TaskManager newTaskManager = new TaskManager();
            
            Console.WriteLine("\nTarefas carregadas do novo gerenciador:");
            newTaskManager.ListAllTasks();
            
            Console.WriteLine("\nEstatísticas do novo gerenciador:");
            newTaskManager.ShowStatistics();

            Console.WriteLine("\n=== PERSISTÊNCIA HÍBRIDA IMPLEMENTADA COM SUCESSO! ===");
            Console.WriteLine("✓ Metadados salvos em JSON (tasks_metadata.json)");
            Console.WriteLine("✓ Conteúdo textual salvo em SQLite (tasks_content.db)");
            Console.WriteLine("✓ Sistema otimizado para grandes volumes de texto");
        }
    }
}