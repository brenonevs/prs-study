using System;

namespace Searchly 
{
    public abstract class Task
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string DifficultyLevel { get; set; }
        public DateTime CreationDate { get; set; }
        public DateTime DueDate { get; set; }
        public bool IsCompleted { get; set; }
        public string TaskType { get; protected set; } = string.Empty;

        protected Task(string name, string description, string difficultyLevel, DateTime creationDate, DateTime dueDate)
        {
            Name = name;
            Description = description;
            DifficultyLevel = difficultyLevel;
            CreationDate = creationDate;
            DueDate = dueDate;
            IsCompleted = false;
        }

        public virtual void MarkAsCompleted()
        {
            IsCompleted = true;
            Console.WriteLine($"Tarefa '{Name}' marcada como concluída!");
        }

        public virtual void MarkAsPending()
        {
            IsCompleted = false;
            Console.WriteLine($"Tarefa '{Name}' marcada como pendente!");
        }

        public abstract string GetTaskSpecificInfo();

        public override string ToString()
        {
            return $"Tipo: {TaskType}\n" +
                   $"Nome: {Name}\n" +
                   $"Descrição: {Description}\n" +
                   $"Dificuldade: {DifficultyLevel}\n" +
                   $"Criada em: {CreationDate.ToShortDateString()}\n" +
                   $"Previsão: {DueDate.ToShortDateString()}\n" +
                   $"Status: {(IsCompleted ? "Concluída" : "Pendente")}\n" +
                   GetTaskSpecificInfo();
        }
    }

    public class WorkTask : Task
    {
        public string Project { get; set; }
        public string Priority { get; set; }

        public WorkTask(string name, string description, string difficultyLevel, DateTime creationDate, DateTime dueDate, string project, string priority)
            : base(name, description, difficultyLevel, creationDate, dueDate)
        {
            TaskType = "Trabalho";
            Project = project;
            Priority = priority;
        }

        public override string GetTaskSpecificInfo()
        {
            return $"Projeto: {Project}\n" +
                   $"Prioridade: {Priority}\n";
        }

        public override void MarkAsCompleted()
        {
            base.MarkAsCompleted();
            Console.WriteLine($"Tarefa de trabalho '{Name}' do projeto '{Project}' finalizada!");
        }
    }

    public class PersonalTask : Task
    {
        public string Category { get; set; }
        public bool IsUrgent { get; set; }

        public PersonalTask(string name, string description, string difficultyLevel, DateTime creationDate, DateTime dueDate, string category, bool isUrgent = false)
            : base(name, description, difficultyLevel, creationDate, dueDate)
        {
            TaskType = "Pessoal";
            Category = category;
            IsUrgent = isUrgent;
        }

        public override string GetTaskSpecificInfo()
        {
            return $"Categoria: {Category}\n" +
                   $"Urgente: {(IsUrgent ? "Sim" : "Não")}\n";
        }

        public override void MarkAsCompleted()
        {
            base.MarkAsCompleted();
            string urgencyText = IsUrgent ? "urgente" : "pessoal";
            Console.WriteLine($"Tarefa {urgencyText} '{Name}' da categoria '{Category}' concluída!");
        }
    }

    public class StudyTask : Task
    {
        public string Subject { get; set; }
        public int StudyHours { get; set; }
        public string StudyMethod { get; set; }

        public StudyTask(string name, string description, string difficultyLevel, DateTime creationDate, DateTime dueDate, string subject, int studyHours, string studyMethod)
            : base(name, description, difficultyLevel, creationDate, dueDate)
        {
            TaskType = "Estudo";
            Subject = subject;
            StudyHours = studyHours;
            StudyMethod = studyMethod;
        }

        public override string GetTaskSpecificInfo()
        {
            return $"Matéria: {Subject}\n" +
                   $"Horas de estudo: {StudyHours}\n" +
                   $"Método: {StudyMethod}\n";
        }

        public override void MarkAsCompleted()
        {
            base.MarkAsCompleted();
            Console.WriteLine($"Sessão de estudo de '{Subject}' concluída! ({StudyHours} horas dedicadas)");
        }
    }

    public class HealthTask : Task
    {
        public string ActivityType { get; set; }
        public int Duration { get; set; }
        public string Location { get; set; }

        public HealthTask(string name, string description, string difficultyLevel, DateTime creationDate, DateTime dueDate, string activityType, int duration, string location)
            : base(name, description, difficultyLevel, creationDate, dueDate)
        {
            TaskType = "Saúde";
            ActivityType = activityType;
            Duration = duration;
            Location = location;
        }

        public override string GetTaskSpecificInfo()
        {
            return $"Tipo de atividade: {ActivityType}\n" +
                   $"Duração: {Duration} minutos\n" +
                   $"Local: {Location}\n";
        }

        public override void MarkAsCompleted()
        {
            base.MarkAsCompleted();
            Console.WriteLine($"Atividade de saúde '{ActivityType}' realizada por {Duration} minutos em {Location}!");
        }
    }
}