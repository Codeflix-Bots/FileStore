import motor.motor_asyncio
from config import DB_URI, DB_NAME
from pytz import timezone
from datetime import datetime, timedelta

# Create an async client with Motor
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]
collection = database['premium-users']

# Check if the user is a premium user
async def is_premium_user(user_id):
    user = await collection.find_one({"user_id": user_id})  # Async query
    return user is not None

# Remove premium user
async def remove_premium(user_id):
    await collection.delete_one({"user_id": user_id})  # Async removal

# Remove expired users
async def remove_expired_users():
    ist = timezone("Asia/Kolkata")
    current_time = datetime.now(ist)

    async for user in collection.find({}):
        expiration = user.get("expiration_timestamp")
        if not expiration:
            continue  # Skip invalid entries

        try:
            expiration_time = datetime.fromisoformat(expiration).astimezone(ist)
            if expiration_time <= current_time:
                await collection.delete_one({"user_id": user["user_id"]})
        except Exception as e:
            print(f"Error removing user {user.get('user_id')}: {e}")



# List active premium users
async def list_premium_users():
    # Define IST timezone
    ist = timezone("Asia/Kolkata")

    # Fetch all premium users from the collection
    premium_users = collection.find({})
    premium_user_list = []

    async for user in premium_users:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]

        # Convert expiration timestamp to a timezone-aware datetime object in IST
        expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)

        # Calculate the remaining time (make sure both are timezone-aware)
        remaining_time = expiration_time - datetime.now(ist)

        if remaining_time.total_seconds() > 0:  # Only active users
            # Calculate days, hours, minutes, and seconds left
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )

            # Format the expiration time in IST and remaining time
            expiry_info = f"{days}d {hours}h {minutes}m {seconds}s left"

            # Format the expiration time for clarity
            formatted_expiry_time = expiration_time.strftime('%Y-%m-%d %H:%M:%S %p IST')

            # Add user info to the list with both remaining and expiration times
            premium_user_list.append(f"UserID: {user_id} - Expiry: {expiry_info} (Expires at {formatted_expiry_time})")

    return premium_user_list

# Add premium user
async def add_premium(user_id, time_value, time_unit):
    """
    Add a premium user for a specific duration.
    
    Args:
        user_id (int): The ID of the user to add premium access for.
        time_value (int): The numeric value of the duration.
        time_unit (str): Time unit - 's'=seconds, 'm'=minutes, 'h'=hours, 'd'=days, 'y'=years.
    """
    # Normalize unit to lowercase
    time_unit = time_unit.lower()

    # Get IST timezone
    ist = timezone("Asia/Kolkata")

    # Calculate expiration time
    now = datetime.now(ist)
    if time_unit == 's':
        expiration_time = now + timedelta(seconds=time_value)
    elif time_unit == 'm':
        expiration_time = now + timedelta(minutes=time_value)
    elif time_unit == 'h':
        expiration_time = now + timedelta(hours=time_value)
    elif time_unit == 'd':
        expiration_time = now + timedelta(days=time_value)
    elif time_unit == 'y':
        expiration_time = now + timedelta(days=365 * time_value)
    else:
        raise ValueError("Invalid time unit. Use 's', 'm', 'h', 'd', or 'y'.")

    # Prepare premium data
    premium_data = {
        "user_id": user_id,
        "expiration_timestamp": expiration_time.isoformat(),
    }

    # Update database
    await collection.update_one(
        {"user_id": user_id},
        {"$set": premium_data},
        upsert=True
    )

    # Format and return
    formatted_expiration = expiration_time.strftime('%Y-%m-%d %H:%M:%S %p IST')
    #print(f"User {user_id} premium access expires on {formatted_expiration}")
    return formatted_expiration



# Check if a user has an active premium plan
async def check_user_plan(user_id):
    user = await collection.find_one({"user_id": user_id})  # Async query for user
    if user:
        expiration_timestamp = user["expiration_timestamp"]
        # Convert expiration timestamp to a timezone-aware datetime object in IST
        expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(timezone("Asia/Kolkata"))
        
        # Calculate the remaining time
        remaining_time = expiration_time - datetime.now(timezone("Asia/Kolkata"))
        
        if remaining_time.total_seconds() > 0:  # If the user is still active
            # Format the remaining time
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            validity_info = f"Your premium plan is active. {days}d {hours}h {minutes}m {seconds}s left."
            return validity_info
        else:
            return "Your premium plan has expired."
    else:
        return "You do not have a premium plan."
