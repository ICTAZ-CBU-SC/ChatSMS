namespace Server.Models
{
    public class SmsMessage
    {
        public string PhoneNumber { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
    }
}