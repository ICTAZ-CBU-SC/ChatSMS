using Microsoft.AspNetCore.Mvc;
using Server.Models;
using Server.Services;

namespace Server.Controllers;

[ApiController]
[Route("[controller]")]
public class RequestController(LlamaService llamaService) : ControllerBase
{
    [HttpPost]
    public async Task<ActionResult<CompletionResponse>> GetResponse(CompletionRequest request)
    {
        var completion = await llamaService.GetCompletionAsync(request.Prompt);
        return new CompletionResponse { Text = completion };
    }
}