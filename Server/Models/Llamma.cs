namespace Server.Models
{
    public class Llamma
    {
        public string ModelPath { get; set; }
        public int ContextSize { get; set; } = 2048;
        public int GpuLayerCount { get; set; } = 0;
    }
    
    public class CompletionRequest
    {
        public string Prompt { get; set; }
    }

    public class CompletionResponse
    {
        public string Text { get; set; }
    }
}