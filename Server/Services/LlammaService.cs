using LLama;
using LLama.Common;
using LLama.Sampling;
using Microsoft.Extensions.Options;
using Server.Models;

namespace Server.Services;
using System.Collections.Generic;

public class LlamaService : IDisposable
{
    private readonly LLamaWeights _model;
    private readonly LLamaContext _context;
    private readonly InteractiveExecutor _executor;
    private readonly ChatSession _chatSession;
    private readonly List<ChatHistory.Message> _conversationHistory = new();
    private bool _disposed = false;

    public LlamaService(IOptions<Llamma> settings)
    {
        var parameters = new ModelParams(settings.Value.ModelPath)
        {
            ContextSize = (uint?)settings.Value.ContextSize,
            GpuLayerCount = settings.Value.GpuLayerCount
        };

        _model = LLamaWeights.LoadFromFile(parameters);
        _context = _model.CreateContext(parameters);
        _executor = new InteractiveExecutor(_context);
        _chatSession = new ChatSession(_executor);
    }

    public async Task<string> GetCompletionAsync(string prompt)
    {
        var inferenceParams = new InferenceParams()
        {
            MaxTokens = 256,
            AntiPrompts = new List<string> { "User:" },
            SamplingPipeline = new DefaultSamplingPipeline(),
        };

        var result = new System.Text.StringBuilder();
        await foreach (var text in _chatSession.ChatAsync(new ChatHistory.Message(AuthorRole.User, prompt), inferenceParams))
        {
            result.Append(text);
        }
        
        return result.ToString();
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                _context?.Dispose();
                _model?.Dispose();
            }
            _disposed = true;
        }
    }
    ~LlamaService()
    {
        Dispose(false);
    }
}
