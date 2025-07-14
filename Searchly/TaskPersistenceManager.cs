using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using Newtonsoft.Json;

namespace Searchly
{

    public class TaskPersistenceManager
    {
        private const string JsonFilePath = "tasks_metadata.json";
        private const string DatabasePath = "tasks_content.db";
        private const string ConnectionString = "Data Source=tasks_content.db;Version=3;";

        public void Initialize()
        {
            CreateDatabaseIfNotExists();
        }

        private void CreateDatabaseIfNotExists()
        {
            using (var connection = new SQLiteConnection(ConnectionString))
            {
                connection.Open();
                
                string createTableSql = @"
                    CREATE TABLE IF NOT EXISTS TaskContent (
                        TaskId TEXT PRIMARY KEY,
                        Name TEXT NOT NULL,
                        Description TEXT,
                        DifficultyLevel TEXT,
                        CreationDate TEXT,
                        DueDate TEXT,
                        IsCompleted INTEGER DEFAULT 0
                    )";

                using (var command = new SQLiteCommand(createTableSql, connection))
                {
                    command.ExecuteNonQuery();
                }
            }
        }

        public void SaveTasks(List<Task> tasks)
        {
            SaveMetadataToJson(tasks);
            SaveContentToDatabase(tasks);
        }

        private void SaveMetadataToJson(List<Task> tasks)
        {
            var metadata = new List<object>();
            
            foreach (var task in tasks)
            {
                metadata.Add(new
                {
                    TaskId = GenerateTaskId(task),
                    Name = task.Name,
                    DifficultyLevel = task.DifficultyLevel,
                    CreationDate = task.CreationDate.ToString("yyyy-MM-dd HH:mm:ss"),
                    DueDate = task.DueDate.ToString("yyyy-MM-dd HH:mm:ss"),
                    IsCompleted = task.IsCompleted
                });
            }

            string json = JsonConvert.SerializeObject(metadata, Formatting.Indented);
            File.WriteAllText(JsonFilePath, json);
        }

        private void SaveContentToDatabase(List<Task> tasks)
        {
            using (var connection = new SQLiteConnection(ConnectionString))
            {
                connection.Open();
                
                using (var deleteCommand = new SQLiteCommand("DELETE FROM TaskContent", connection))
                {
                    deleteCommand.ExecuteNonQuery();
                }

                string insertSql = @"
                    INSERT INTO TaskContent (TaskId, Name, Description, DifficultyLevel, CreationDate, DueDate, IsCompleted)
                    VALUES (@TaskId, @Name, @Description, @DifficultyLevel, @CreationDate, @DueDate, @IsCompleted)";

                using (var command = new SQLiteCommand(insertSql, connection))
                {
                    foreach (var task in tasks)
                    {
                        command.Parameters.Clear();
                        command.Parameters.AddWithValue("@TaskId", GenerateTaskId(task));
                        command.Parameters.AddWithValue("@Name", task.Name);
                        command.Parameters.AddWithValue("@Description", task.Description);
                        command.Parameters.AddWithValue("@DifficultyLevel", task.DifficultyLevel);
                        command.Parameters.AddWithValue("@CreationDate", task.CreationDate.ToString("yyyy-MM-dd HH:mm:ss"));
                        command.Parameters.AddWithValue("@DueDate", task.DueDate.ToString("yyyy-MM-dd HH:mm:ss"));
                        command.Parameters.AddWithValue("@IsCompleted", task.IsCompleted ? 1 : 0);
                        
                        command.ExecuteNonQuery();
                    }
                }
            }
        }

        public List<Task> LoadTasks()
        {
            var tasks = new List<Task>();
            
            if (!File.Exists(JsonFilePath) || !File.Exists(DatabasePath))
            {
                return tasks;
            }

            try
            {
                // Carrega metadados do JSON
                string jsonContent = File.ReadAllText(JsonFilePath);
                var metadata = JsonConvert.DeserializeObject<List<dynamic>>(jsonContent);

                // Carrega conteúdo do SQLite
                using (var connection = new SQLiteConnection(ConnectionString))
                {
                    connection.Open();
                    
                    string selectSql = "SELECT * FROM TaskContent";
                    using (var command = new SQLiteCommand(selectSql, connection))
                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            var name = reader["Name"]?.ToString() ?? "";
                            var description = reader["Description"]?.ToString() ?? "";
                            var difficultyLevel = reader["DifficultyLevel"]?.ToString() ?? "";
                            var creationDateStr = reader["CreationDate"]?.ToString() ?? "";
                            var dueDateStr = reader["DueDate"]?.ToString() ?? "";

                            if (!string.IsNullOrEmpty(name) && 
                                !string.IsNullOrEmpty(creationDateStr) && 
                                !string.IsNullOrEmpty(dueDateStr))
                            {
                                var task = new Task(
                                    name,
                                    description,
                                    difficultyLevel,
                                    DateTime.Parse(creationDateStr),
                                    DateTime.Parse(dueDateStr)
                                );

                                task.IsCompleted = Convert.ToBoolean(reader["IsCompleted"]);
                                tasks.Add(task);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro ao carregar tarefas: {ex.Message}");
            }

            return tasks;
        }

        public void UpdateTask(Task task)
        {
            using (var connection = new SQLiteConnection(ConnectionString))
            {
                connection.Open();
                
                string updateSql = @"
                    UPDATE TaskContent 
                    SET Name = @Name, Description = @Description, DifficultyLevel = @DifficultyLevel,
                        CreationDate = @CreationDate, DueDate = @DueDate, IsCompleted = @IsCompleted
                    WHERE TaskId = @TaskId";

                using (var command = new SQLiteCommand(updateSql, connection))
                {
                    command.Parameters.AddWithValue("@TaskId", GenerateTaskId(task));
                    command.Parameters.AddWithValue("@Name", task.Name);
                    command.Parameters.AddWithValue("@Description", task.Description);
                    command.Parameters.AddWithValue("@DifficultyLevel", task.DifficultyLevel);
                    command.Parameters.AddWithValue("@CreationDate", task.CreationDate.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@DueDate", task.DueDate.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@IsCompleted", task.IsCompleted ? 1 : 0);
                    
                    command.ExecuteNonQuery();
                }
            }

            var allTasks = LoadTasks();
            SaveMetadataToJson(allTasks);
        }


        public void RemoveTask(Task task)
        {
            using (var connection = new SQLiteConnection(ConnectionString))
            {
                connection.Open();
                
                string deleteSql = "DELETE FROM TaskContent WHERE TaskId = @TaskId";
                using (var command = new SQLiteCommand(deleteSql, connection))
                {
                    command.Parameters.AddWithValue("@TaskId", GenerateTaskId(task));
                    command.ExecuteNonQuery();
                }
            }

            var allTasks = LoadTasks();
            SaveMetadataToJson(allTasks);
        }

        private string GenerateTaskId(Task task)
        {
            return $"{task.Name}_{task.CreationDate:yyyyMMddHHmmss}";
        }


        public bool HasPersistedData()
        {
            return File.Exists(JsonFilePath) && File.Exists(DatabasePath);
        }

        public void ClearAllData()
        {
            if (File.Exists(JsonFilePath))
                File.Delete(JsonFilePath);
                
            if (File.Exists(DatabasePath))
                File.Delete(DatabasePath);
        }
    }
} 