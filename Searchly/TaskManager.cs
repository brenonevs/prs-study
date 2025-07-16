using System;
using System.Collections.Generic;
using System.Linq;

namespace Searchly
{

    public class TaskManager
    {
        private List<Task> _tasks = new List<Task>();
        private TaskPersistenceManager _persistenceManager;

        public TaskManager()
        {
            _persistenceManager = new TaskPersistenceManager();
            _persistenceManager.Initialize();
            LoadTasksFromPersistence();
        }
        
        private void LoadTasksFromPersistence()
        {
            if (_persistenceManager.HasPersistedData())
            {
                _tasks = _persistenceManager.LoadTasks();
                Console.WriteLine($"Carregadas {_tasks.Count} tarefas da persistência.");
            }
        }

        public void AddTask(Task task)
        {
            _tasks.Add(task);
            _persistenceManager.SaveTasks(_tasks);
            Console.WriteLine($"Tarefa '{task.Name}' adicionada com sucesso!");
        }

        public void RemoveTask(Task task)
        {
            _tasks.Remove(task);
            _persistenceManager.RemoveTask(task);
            Console.WriteLine($"Tarefa '{task.Name}' removida com sucesso!");
        }

        public void ListAllTasks()
        {
            if (_tasks.Count == 0)
            {
                Console.WriteLine("Nenhuma tarefa encontrada.");
                return;
            }

            Console.WriteLine($"\n=== LISTA DE TAREFAS ({_tasks.Count} tarefas) ===\n");
            for (int i = 0; i < _tasks.Count; i++)
            {
                Console.WriteLine($"\n\n--- Tarefa {i + 1} ---");
                Console.WriteLine(_tasks[i].ToString());
            }
        }

        public void ListPendingTasks()
        {
            var pendingTasks = _tasks.Where(t => !t.IsCompleted).ToList();
            
            if (pendingTasks.Count == 0)
            {
                Console.WriteLine("Nenhuma tarefa pendente encontrada.");
                return;
            }

            Console.WriteLine($"\n=== TAREFAS PENDENTES ({pendingTasks.Count} tarefas) ===\n");
            for (int i = 0; i < pendingTasks.Count; i++)
            {
                Console.WriteLine($"--- Tarefa {i + 1} ---");
                Console.WriteLine(pendingTasks[i].ToString());
            }
        }

        public void ListCompletedTasks()
        {
            var completedTasks = _tasks.Where(t => t.IsCompleted).ToList();
            
            if (completedTasks.Count == 0)
            {
                Console.WriteLine("Nenhuma tarefa concluída encontrada.");
                return;
            }

            Console.WriteLine($"\n=== TAREFAS CONCLUÍDAS ({completedTasks.Count} tarefas) ===\n");
            for (int i = 0; i < completedTasks.Count; i++)
            {
                Console.WriteLine($"--- Tarefa {i + 1} ---");
                Console.WriteLine(completedTasks[i].ToString());
            }
        }

        public Task? FindTaskByName(string name)
        {
            return _tasks.FirstOrDefault(t => 
                t.Name.Equals(name, StringComparison.OrdinalIgnoreCase));
        }

        public bool RemoveTaskByName(string name)
        {
            var task = FindTaskByName(name);
            if (task != null)
            {
                RemoveTask(task);
                return true;
            }
            
            Console.WriteLine($"Tarefa '{name}' não encontrada.");
            return false;
        }

        public bool CompleteTaskByName(string name)
        {
            var task = FindTaskByName(name);
            if (task != null)
            {
                task.MarkAsCompleted();
                _persistenceManager.UpdateTask(task);
                return true;
            }
            
            Console.WriteLine($"Tarefa '{name}' não encontrada.");
            return false;
        }

        public void ShowStatistics()
        {
            int total = _tasks.Count;
            int completed = _tasks.Count(t => t.IsCompleted);
            int pending = total - completed;
            double completionRate = total > 0 ? (double)completed / total * 100 : 0;

            Console.WriteLine("\n=== ESTATÍSTICAS ===");
            Console.WriteLine($"Total de tarefas: {total}");
            Console.WriteLine($"Tarefas concluídas: {completed}");
            Console.WriteLine($"Tarefas pendentes: {pending}");
            Console.WriteLine($"Taxa de conclusão: {completionRate:F1}%");
        }

        public int GetTaskCount()
        {
            return _tasks.Count;
        }

        public bool HasTasks()
        {
            return _tasks.Count > 0;
        }

        public void SaveAllTasks()
        {
            _persistenceManager.SaveTasks(_tasks);
            Console.WriteLine("Todas as tarefas foram salvas na persistência.");
        }

        public void ReloadTasks()
        {
            _tasks = _persistenceManager.LoadTasks();
            Console.WriteLine($"Recarregadas {_tasks.Count} tarefas da persistência.");
        }

        public void ClearPersistedData()
        {
            _persistenceManager.ClearAllData();
            _tasks.Clear();
            Console.WriteLine("Todos os dados persistidos foram limpos.");
        }
    }

}
