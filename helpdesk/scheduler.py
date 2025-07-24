from apscheduler.schedulers.background import BackgroundScheduler
from horilla.utils.logger import HorillaLogger
from helpdesk.models import Ticket
from datetime import datetime, timedelta
from helpdesk.utils import CreateTicket
import os
from croniter import croniter

logger = HorillaLogger("horilla.helpdesk.scheduler")


def parse_cron_expression(cron_expr):
    """
    Parse a CRON expression into APScheduler parameters.
    Returns a dictionary of parameters for the scheduler.
    """
    # Split the CRON expression into its components
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError("Invalid CRON expression format. Expected 5 parts: minute hour day month weekday")
    
    minute, hour, day, month, weekday = parts
    
    # Convert to APScheduler parameters
    params = {}
    if minute != '*':
        params['minute'] = minute
    if hour != '*':
        params['hour'] = hour
    if day != '*':
        params['day'] = day
    if month != '*':
        params['month'] = month
    if weekday != '*':
        params['day_of_week'] = weekday
    
    logger.info(f"Params ======= : {params}")
    return params



def FrequencyTicketScheduler(ticket_id=None):
    """
    This function is used to create new tickets based on the frequency of existing tickets.
    """
    logger.info(f"Frequency Ticket Scheduler started with query: {Ticket.objects.get(id=ticket_id)}")
    if ticket_id:
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if ticket.frequency == "custom":
                # For custom CRON, we don't check deadline as it's handled by the CRON expression
                logger.info(f"Creating new ticket from custom CRON: {ticket.title}")
                CreateTicket(ticket)
            elif ticket.frequency and ticket.deadline == datetime.now().date():
                logger.info(f"Creating new ticket: {ticket.title}")
                CreateTicket(ticket)
        except Ticket.DoesNotExist:
            logger.warning(f"Ticket with id {ticket_id} does not exist.")
    else:
        logger.warning("No ticket_id provided to scheduler.")


            
def start():
    logger.info("initiated Frequency Ticket Scheduler")
    scheduler = BackgroundScheduler()
    try:
        tickets = Ticket.objects.all()
    except Exception as e:
        logger.error(f"Failed to fetch tickets: {e}")
        return

    logger.info(f"Tickets inside the scheduler start ======== : {tickets}")
    for ticket in tickets:
        logger.info(f"Ticket started ======== : {ticket}")
        job_id = f"ticket_scheduler_{ticket.id}"
        logger.info(f"Job ID: {job_id}")
        
        if ticket.frequency == "custom" and ticket.cron_expression:
            try:
                # Validate CRON expression
                croniter(ticket.cron_expression)
                scheduler.add_job(
                    FrequencyTicketScheduler,
                    trigger="cron",
                    id=job_id,
                    replace_existing=True,
                    kwargs={'ticket_id': ticket.id},
                    **parse_cron_expression(ticket.cron_expression)
                )
                logger.info(f"Ticket {ticket.title} added to scheduler with custom CRON: {ticket.cron_expression}")
            except Exception as e:
                logger.error(f"Invalid CRON expression for ticket {ticket.id}: {e}")
        else:
            scheduler.add_job(
                FrequencyTicketScheduler,
                trigger="cron",
                hour=1,
                minute=30,
                id=job_id, 
                replace_existing=True,
                kwargs={'ticket_id': ticket.id}
            )
            logger.info(f"Ticket {ticket.title} added to scheduler with time 1:30 UTC")
    
    try:
        scheduler.start()
        logger.info("Frequency Ticket Scheduler started successfully")
        for ticket in tickets:
            job_id = f"ticket_scheduler_{ticket.id}"
            job = scheduler.get_job(job_id)
            if job and job.next_run_time:
                logger.info(f"Next run time for ticket '{ticket.title}' (job ID {job_id}): {job.next_run_time}")
            else:
                logger.warning(f"Job {job_id} has no next run time yet.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        return
