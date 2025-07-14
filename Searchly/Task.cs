using System;

namespace Searchly 
{
    public class Task
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string DifficultyLevel { get; set; }
        public DateTime CreationDate { get; set; }
        public DateTime DueDate { get; set; }
        public bool IsCompleted { get; set; }

        public Task(string name, string description, string difficultyLevel, DateTime creationDate, DateTime dueDate)
        {
            Name = name;
            Description = description;
            DifficultyLevel = difficultyLevel;
            CreationDate = creationDate;
            DueDate = dueDate;
            IsCompleted = false;
        }

        public void MarkAsCompleted()
        {
            IsCompleted = true;
            Console.WriteLine($"Tarefa '{Name}' marcada como concluída!");
        }

        public void MarkAsPending()
        {
            IsCompleted = false;
            Console.WriteLine($"Tarefa '{Name}' marcada como pendente!");
        }

        public override string ToString()
        {
            return $"Nome: {Name}\n" +
                   $"Descrição: {Description}\n" +
                   $"Dificuldade: {DifficultyLevel}\n" +
                   $"Criada em: {CreationDate.ToShortDateString()}\n" +
                   $"Previsão: {DueDate.ToShortDateString()}\n" +
                   $"Status: {(IsCompleted ? "Concluída" : "Pendente")}\n";
        }
    }
}