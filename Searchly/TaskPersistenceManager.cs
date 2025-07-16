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
                
                bool needsRecreation = false;
                
                try
                {
                    using (var command = new SQLiteCommand("SELECT TaskType FROM TaskContent LIMIT 1", connection))
                    {
                        command.ExecuteScalar();
                    }
                }
                catch
                {
                    needsRecreation = true;
                }
                
                if (needsRecreation)
                {
                    using (var dropCommand = new SQLiteCommand("DROP TABLE IF EXISTS TaskContent", connection))
                    {
                        dropCommand.ExecuteNonQuery();
                    }
                }
                
                string createTableSql = @"
                    CREATE TABLE IF NOT EXISTS TaskContent (
                        TaskId TEXT PRIMARY KEY,
                        TaskType TEXT NOT NULL,
                        Name TEXT NOT NULL,
                        Description TEXT,
                        DifficultyLevel TEXT,
                        CreationDate TEXT,
                        DueDate TEXT,
                        IsCompleted INTEGER DEFAULT 0,
                        Project TEXT,
                        Priority TEXT,
                        Category TEXT,
                        IsUrgent INTEGER DEFAULT 0,
                        Subject TEXT,
                        StudyHours INTEGER DEFAULT 0,
                        StudyMethod TEXT,
                        ActivityType TEXT,
                        Duration INTEGER DEFAULT 0,
                        Location TEXT
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
                var baseMetadata = new
                {
                    TaskId = GenerateTaskId(task),
                    TaskType = task.TaskType,
                    Name = task.Name,
                    DifficultyLevel = task.DifficultyLevel,
                    CreationDate = task.CreationDate.ToString("yyyy-MM-dd HH:mm:ss"),
                    DueDate = task.DueDate.ToString("yyyy-MM-dd HH:mm:ss"),
                    IsCompleted = task.IsCompleted
                };

                metadata.Add(baseMetadata);
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
                    INSERT INTO TaskContent (TaskId, TaskType, Name, Description, DifficultyLevel, CreationDate, DueDate, IsCompleted, 
                                           Project, Priority, Category, IsUrgent, Subject, StudyHours, StudyMethod, ActivityType, Duration, Location)
                    VALUES (@TaskId, @TaskType, @Name, @Description, @DifficultyLevel, @CreationDate, @DueDate, @IsCompleted,
                           @Project, @Priority, @Category, @IsUrgent, @Subject, @StudyHours, @StudyMethod, @ActivityType, @Duration, @Location)";

                using (var command = new SQLiteCommand(insertSql, connection))
                {
                    foreach (var task in tasks)
                    {
                        command.Parameters.Clear();
                        command.Parameters.AddWithValue("@TaskId", GenerateTaskId(task));
                        command.Parameters.AddWithValue("@TaskType", task.TaskType);
                        command.Parameters.AddWithValue("@Name", task.Name);
                        command.Parameters.AddWithValue("@Description", task.Description);
                        command.Parameters.AddWithValue("@DifficultyLevel", task.DifficultyLevel);
                        command.Parameters.AddWithValue("@CreationDate", task.CreationDate.ToString("yyyy-MM-dd HH:mm:ss"));
                        command.Parameters.AddWithValue("@DueDate", task.DueDate.ToString("yyyy-MM-dd HH:mm:ss"));
                        command.Parameters.AddWithValue("@IsCompleted", task.IsCompleted ? 1 : 0);
                        
                        command.Parameters.AddWithValue("@Project", DBNull.Value);
                        command.Parameters.AddWithValue("@Priority", DBNull.Value);
                        command.Parameters.AddWithValue("@Category", DBNull.Value);
                        command.Parameters.AddWithValue("@IsUrgent", DBNull.Value);
                        command.Parameters.AddWithValue("@Subject", DBNull.Value);
                        command.Parameters.AddWithValue("@StudyHours", DBNull.Value);
                        command.Parameters.AddWithValue("@StudyMethod", DBNull.Value);
                        command.Parameters.AddWithValue("@ActivityType", DBNull.Value);
                        command.Parameters.AddWithValue("@Duration", DBNull.Value);
                        command.Parameters.AddWithValue("@Location", DBNull.Value);

                        if (task is WorkTask workTask)
                        {
                            command.Parameters["@Project"].Value = workTask.Project;
                            command.Parameters["@Priority"].Value = workTask.Priority;
                        }
                        else if (task is PersonalTask personalTask)
                        {
                            command.Parameters["@Category"].Value = personalTask.Category;
                            command.Parameters["@IsUrgent"].Value = personalTask.IsUrgent ? 1 : 0;
                        }
                        else if (task is StudyTask studyTask)
                        {
                            command.Parameters["@Subject"].Value = studyTask.Subject;
                            command.Parameters["@StudyHours"].Value = studyTask.StudyHours;
                            command.Parameters["@StudyMethod"].Value = studyTask.StudyMethod;
                        }
                        else if (task is HealthTask healthTask)
                        {
                            command.Parameters["@ActivityType"].Value = healthTask.ActivityType;
                            command.Parameters["@Duration"].Value = healthTask.Duration;
                            command.Parameters["@Location"].Value = healthTask.Location;
                        }
                        
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
                string jsonContent = File.ReadAllText(JsonFilePath);
                var metadata = JsonConvert.DeserializeObject<List<dynamic>>(jsonContent);
                
                using (var connection = new SQLiteConnection(ConnectionString))
                {
                    connection.Open();
                    
                    string selectSql = "SELECT * FROM TaskContent";
                    using (var command = new SQLiteCommand(selectSql, connection))
                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            var taskType = reader["TaskType"]?.ToString() ?? "";
                            var name = reader["Name"]?.ToString() ?? "";
                            var description = reader["Description"]?.ToString() ?? "";
                            var difficultyLevel = reader["DifficultyLevel"]?.ToString() ?? "";
                            var creationDateStr = reader["CreationDate"]?.ToString() ?? "";
                            var dueDateStr = reader["DueDate"]?.ToString() ?? "";

                            if (!string.IsNullOrEmpty(name) && 
                                !string.IsNullOrEmpty(creationDateStr) && 
                                !string.IsNullOrEmpty(dueDateStr))
                            {
                                Task? task = CreateTaskByType(taskType, name, description, difficultyLevel, 
                                                          DateTime.Parse(creationDateStr), DateTime.Parse(dueDateStr), reader);
                                
                                if (task != null)
                                {
                                    task.IsCompleted = Convert.ToBoolean(reader["IsCompleted"]);
                                    tasks.Add(task);
                                }
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

        private Task? CreateTaskByType(string taskType, string name, string description, string difficultyLevel, 
                                    DateTime creationDate, DateTime dueDate, SQLiteDataReader reader)
        {
            switch (taskType)
            {
                case "Trabalho":
                    var project = reader["Project"]?.ToString() ?? "";
                    var priority = reader["Priority"]?.ToString() ?? "";
                    return new WorkTask(name, description, difficultyLevel, creationDate, dueDate, project, priority);
                
                case "Pessoal":
                    var category = reader["Category"]?.ToString() ?? "";
                    var isUrgent = Convert.ToBoolean(reader["IsUrgent"]);
                    return new PersonalTask(name, description, difficultyLevel, creationDate, dueDate, category, isUrgent);
                
                case "Estudo":
                    var subject = reader["Subject"]?.ToString() ?? "";
                    var studyHours = Convert.ToInt32(reader["StudyHours"]);
                    var studyMethod = reader["StudyMethod"]?.ToString() ?? "";
                    return new StudyTask(name, description, difficultyLevel, creationDate, dueDate, subject, studyHours, studyMethod);
                
                case "Saúde":
                    var activityType = reader["ActivityType"]?.ToString() ?? "";
                    var duration = Convert.ToInt32(reader["Duration"]);
                    var location = reader["Location"]?.ToString() ?? "";
                    return new HealthTask(name, description, difficultyLevel, creationDate, dueDate, activityType, duration, location);
                
                default:
                    return null;
            }
        }

        public void UpdateTask(Task task)
        {
            using (var connection = new SQLiteConnection(ConnectionString))
            {
                connection.Open();
                
                string updateSql = @"
                    UPDATE TaskContent 
                    SET TaskType = @TaskType, Name = @Name, Description = @Description, DifficultyLevel = @DifficultyLevel,
                        CreationDate = @CreationDate, DueDate = @DueDate, IsCompleted = @IsCompleted,
                        Project = @Project, Priority = @Priority, Category = @Category, IsUrgent = @IsUrgent,
                        Subject = @Subject, StudyHours = @StudyHours, StudyMethod = @StudyMethod,
                        ActivityType = @ActivityType, Duration = @Duration, Location = @Location
                    WHERE TaskId = @TaskId";

                using (var command = new SQLiteCommand(updateSql, connection))
                {
                    command.Parameters.AddWithValue("@TaskId", GenerateTaskId(task));
                    command.Parameters.AddWithValue("@TaskType", task.TaskType);
                    command.Parameters.AddWithValue("@Name", task.Name);
                    command.Parameters.AddWithValue("@Description", task.Description);
                    command.Parameters.AddWithValue("@DifficultyLevel", task.DifficultyLevel);
                    command.Parameters.AddWithValue("@CreationDate", task.CreationDate.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@DueDate", task.DueDate.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@IsCompleted", task.IsCompleted ? 1 : 0);
                    
                    command.Parameters.AddWithValue("@Project", DBNull.Value);
                    command.Parameters.AddWithValue("@Priority", DBNull.Value);
                    command.Parameters.AddWithValue("@Category", DBNull.Value);
                    command.Parameters.AddWithValue("@IsUrgent", DBNull.Value);
                    command.Parameters.AddWithValue("@Subject", DBNull.Value);
                    command.Parameters.AddWithValue("@StudyHours", DBNull.Value);
                    command.Parameters.AddWithValue("@StudyMethod", DBNull.Value);
                    command.Parameters.AddWithValue("@ActivityType", DBNull.Value);
                    command.Parameters.AddWithValue("@Duration", DBNull.Value);
                    command.Parameters.AddWithValue("@Location", DBNull.Value);

                    if (task is WorkTask workTask)
                    {
                        command.Parameters["@Project"].Value = workTask.Project;
                        command.Parameters["@Priority"].Value = workTask.Priority;
                    }
                    else if (task is PersonalTask personalTask)
                    {
                        command.Parameters["@Category"].Value = personalTask.Category;
                        command.Parameters["@IsUrgent"].Value = personalTask.IsUrgent ? 1 : 0;
                    }
                    else if (task is StudyTask studyTask)
                    {
                        command.Parameters["@Subject"].Value = studyTask.Subject;
                        command.Parameters["@StudyHours"].Value = studyTask.StudyHours;
                        command.Parameters["@StudyMethod"].Value = studyTask.StudyMethod;
                    }
                    else if (task is HealthTask healthTask)
                    {
                        command.Parameters["@ActivityType"].Value = healthTask.ActivityType;
                        command.Parameters["@Duration"].Value = healthTask.Duration;
                        command.Parameters["@Location"].Value = healthTask.Location;
                    }
                    
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
            return $"{task.TaskType}_{task.Name}_{task.CreationDate:yyyyMMddHHmmss}";
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