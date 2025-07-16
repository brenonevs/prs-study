using System;
using Searchly;

namespace Searchly 
{

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== BEM-VINDO AO GERENCIADOR DE TAREFAS COM PERSISTÊNCIA HÍBRIDA E HERANÇA ===\n");

            TaskManager taskManager = new TaskManager();

            Console.WriteLine("=== ADICIONANDO DIFERENTES TIPOS DE TAREFAS ===\n");
            
            StudyTask studyTask = new StudyTask(
                "Estudar C# e POO",
                "Revisar os conceitos de classes, objetos, herança, polimorfismo, encapsulamento e abstração. Focar especialmente em interfaces e classes abstratas.",
                "Médio",
                DateTime.Now,
                DateTime.Now.AddDays(10),
                "Programação",
                8,
                "Prática e teoria"
            );

            PersonalTask shoppingTask = new PersonalTask(
                "Fazer compras",
                "Comprar leite, pão, ovos, frutas, verduras, carne e produtos de limpeza para a semana",
                "Baixa",
                DateTime.Now,
                DateTime.Now.AddDays(2),
                "Casa",
                false
            );
            
            HealthTask gymTask = new HealthTask(
                "Ir na academia",
                "Fazer 1 hora de musculação focando em pernas e glúteos. Incluir exercícios de cardio por 20 minutos",
                "Média",
                DateTime.Now,
                DateTime.Now.AddDays(1),
                "Musculação",
                80,
                "Academia Fitness"
            );

            WorkTask meetingTask = new WorkTask(
                "Reunião com Juju",
                "Reunião com Juju para discutir sobre API e arquitetura do sistema. Preparar apresentação dos pontos principais",
                "Alta",
                DateTime.Now,
                DateTime.Now.AddDays(7),
                "Sistema Searchly",
                "Alta"
            );

            PersonalTask urgentTask = new PersonalTask(
                "Organizar agenda pois Juju vai pedir",
                "Organizar minha agenda com meus horários ONLINE!!! Incluir reuniões, compromissos e tempo para desenvolvimento",
                "Baixa",
                DateTime.Now,
                DateTime.Now.AddDays(3),
                "Organização",
                true
            );

            taskManager.AddTask(studyTask);
            taskManager.AddTask(shoppingTask);
            taskManager.AddTask(gymTask);
            taskManager.AddTask(meetingTask);
            taskManager.AddTask(urgentTask);

            taskManager.ListAllTasks();

            taskManager.ShowStatistics();

            Console.WriteLine("\n=== CONCLUINDO TAREFAS ===\n");
            taskManager.CompleteTaskByName("Fazer compras");
            taskManager.CompleteTaskByName("Ir na academia");

            taskManager.ListPendingTasks();

            taskManager.ListCompletedTasks();

            taskManager.ShowStatistics();

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

            Console.WriteLine("\n=== REMOVENDO TAREFA ===\n");
            taskManager.RemoveTaskByName("Reunião com Juju");
            taskManager.ListAllTasks();

            taskManager.RemoveTaskByName("Tarefa inexistente");

            taskManager.CompleteTaskByName("Tarefa que não existe");

            taskManager.ShowStatistics();

            Console.WriteLine($"\nTotal de tarefas: {taskManager.GetTaskCount()}");
            Console.WriteLine($"Existem tarefas? {taskManager.HasTasks()}");

            taskManager.CompleteTaskByName("Estudar C# e POO");
            taskManager.ListAllTasks();
            taskManager.ShowStatistics();

            taskManager.ListPendingTasks();

            taskManager.ListCompletedTasks();

            Console.WriteLine("\n=== DEMONSTRAÇÃO DA PERSISTÊNCIA HÍBRIDA ===\n");
            
            Console.WriteLine("Salvando todas as tarefas na persistência...");
            taskManager.SaveAllTasks();
            
            Console.WriteLine("\nCriando novo gerenciador para demonstrar carregamento...");
            TaskManager newTaskManager = new TaskManager();
            
            Console.WriteLine("\nTarefas carregadas do novo gerenciador:");
            newTaskManager.ListAllTasks();
            
            Console.WriteLine("\nEstatísticas do novo gerenciador:");
            newTaskManager.ShowStatistics();

        }
    }
}