using Microsoft.AspNetCore.Mvc;
using Server.Models;
using Server.Services;

//using Server.Services;

namespace Server.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SmsRequestController(ILogger<SmsRequestController> logger, LlamaService llamaService) : ControllerBase
    {
        [HttpPost]
        public IActionResult SendSms([FromBody] SmsMessage smsMessage)
        {
            // Here you would typically call a service to send the SMS
            // For example: _smsService.SendSms(smsMessage.PhoneNumber, smsMessage.Message);

            // For demonstration purposes, we'll just log the message and return a success response
            logger.LogInformation($"Sending SMS to {smsMessage.PhoneNumber}: {smsMessage.Message}");

            return Ok(new { Status = "Success", Message = "SMS sent successfully." });
        }

        [HttpPost("receive")]
        public async Task<IActionResult> ProcessPrompt([FromBody] SmsMessage request)
        {
            logger.LogInformation($"Received prompt: {request.Message}"); 

            try
            {
                var response = await llamaService.GetCompletionAsync(request.Message);

                return Ok(new
                {
                    success = true,
                    response
                });
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error processing prompt");
                return StatusCode(500, new { success = false, message = "Error processing prompt" });
            }
        }
    }
    
    
}