using LLama;
using LLama.Common;
using Microsoft.Extensions.Options;
using Server.Models;

namespace Server.Services;
using System.Collections.Generic;

public class LlamaService
{
    private readonly ChatSession _chatSession;
    private readonly List<ChatHistory.Message> _conversationHistory = new();

    public LlamaService(IOptions<Llamma> settings)
    {
        var parameters = new ModelParams(settings.Value.ModelPath)
        {
            ContextSize = (uint?)settings.Value.ContextSize,
            GpuLayerCount = settings.Value.GpuLayerCount
        };

        var model = LLamaWeights.LoadFromFile(parameters);
        var context = model.CreateContext(parameters);
        var executor = new InteractiveExecutor(context);

        _chatSession = new ChatSession(executor);
    }

    public async Task<string> GetCompletionAsync(string prompt)
    {
        if (_conversationHistory.LastOrDefault()?.AuthorRole == AuthorRole.User)
        {
            _conversationHistory.Add(new ChatHistory.Message(AuthorRole.Assistant, "Acknowledged."));
        }

        var userMessage = new ChatHistory.Message(AuthorRole.User, prompt);
        _conversationHistory.Add(userMessage);

        await foreach (var response in _chatSession.ChatAsync(userMessage))
        {
            _conversationHistory.Add(new ChatHistory.Message(AuthorRole.Assistant, response));
            return response; 
        }
        return string.Empty; 
    }
}