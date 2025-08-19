"""An action that sends a simulated confirmation email to the user."""

import logging
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class SendConfirmationEmail(Action):
    """An action that sends a simulated confirmation email."""

    def __init__(self) -> None:
        """Initialize the SendConfirmationEmail action."""
        super().__init__(description="Simulates sending a confirmation email to the user with booking details.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by 'sending' the email."""

        # Get the email address from parameters
        email = params.get("email")
        if not email:
            msg = "Email address is required to send a confirmation."
            raise ValueError(msg)

        # The `context.last_result` will contain the booking details
        if context.last_result.is_empty():
            msg = "No booking context to send a confirmation email for."
            raise ValueError(msg)

        booking_details = context.last_result.as_json_pretty()

        # In a real application, you would use a real email service.
        # Here, we just log the event.
        # Does logging like this work? Sorry if it doesn't Ned
        logging.getLogger("textual_app").info(
            f"Simulating sending confirmation email to {email} with the following details:\n{booking_details}"
        )

        res = ActionResult()
        res.set_param("response", "email_sent_simulated")
        return res

        # Code for sending an actual email if we had a server...
        # Create the email message
        #         msg = EmailMessage()
        #         msg['Subject'] = "Your Trip Confirmation Details"
        #         msg['From'] = self.sender_email
        #         msg['To'] = recipient_email

        # You can use a simple text body or a more formatted HTML body
        #         email_body = f"""
        # Hello,
        # Thank you for booking your trip with us! Here are your confirmation details:

        # {booking_details_json}

        # We hope you have a wonderful trip!
        # Best regards,
        # The Travel Planner Team
        # """
        #         msg.set_content(email_body)

        #         # Connect to the SMTP server and send the email
        #         try:
        #             logging.getLogger("textual_app").info(f"Attempting to send email to {recipient_email}.")

        #             # Create a secure SSL context
        #             context = ssl.create_default_context()

        #             with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        #                 server.starttls(context=context) # Secure the connection
        #                 server.login(self.sender_email, self.sender_password)
        #                 server.send_message(msg)

        #             logging.getLogger("textual_app").info(f"Successfully sent confirmation email to {recipient_email}.")

        #             res = ActionResult()
        #             res.set_param("status", "email_sent_successfully")
        #             return res

        #         except smtplib.SMTPAuthenticationError:
        #             msg = "Failed to log in to the SMTP server. Check your email and app password."
        #             logging.getLogger("textual_app").error(msg)
        #             raise ValueError(msg)
        #         except Exception as e:
        #             msg = f"An error occurred while sending the email: {e}"
        #             logging.getLogger("textual_app").error(msg)
        #             raise ValueError(msg)
