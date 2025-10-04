"""Run the network server."""

# TODO: Run the HTTP server for the REST API and/or WebSocket connection for real-time communication if you have aura.
# use fastapi or something idk

# the endpoints you kinda need are
# - GET /friends?key=TOKEN - get the list of friends for the user (some SQL db needed for this)
# - POST /message/{friend_name/id}/key=TOKEN - send a message to a friend's assistant agent
# - GET /agents/{friend_name/id}/?key=TOKEN - get the list of agents for a friend

# and then stuff for logging in, signing up, sending friend requests etc. (but idk you can cook this how you want)

# - POST /login?username=USERNAME&password=PASSWORD - log in and get the token
# - POST /signup?username=USERNAME&password=PASSWORD - sign up and get the token
# - POST /friend_request/{friend_name/id}/?key=TOKEN - send a friend request to a user
# - POST /accept_friend_request/{friend_name/id}/ - accept a friend request from a user
