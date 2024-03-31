

class CallEvent:
    def __init__(self, from_user, to_user, timestamp):
        self.from_user = from_user
        self.to_user = to_user
        self.timestamp = timestamp


class Call(CallEvent):
    pass


class Hangup(CallEvent):
    pass


def update_call_duration(call_duration, user, duration):
    # Initializes call_duration if it's their first time making call
    if user not in call_duration:
        call_duration[user] = [0, 0]
    call_duration[user][0] += duration
    call_duration[user][1] += 1


def calculate_average_call_duration(call_events):
    call_start_times = {}  # {caller: start_time}
    call_duration = {}  # {caller: [total_duration, call_count]}
    ongoing_calls = set()  # Keep track of ongoing calls as pairs (from_user, to_user)

    for event in call_events:
        if isinstance(event, Call):
            # Store the start time for the caller
            call_start_times[event.from_user] = event.timestamp
            ongoing_calls.add((event.from_user, event.to_user))

        elif isinstance(event, Hangup):
            # Check if the hangup corresponds to a valid ongoing call
            caller_pair = (event.from_user, event.to_user)
            callee_pair = (event.to_user, event.from_user)
            if caller_pair in ongoing_calls or callee_pair in ongoing_calls:
                # Case where person hanging up is the caller
                start_time = call_start_times.get(event.from_user, None)
                if start_time is not None:
                    duration = event.timestamp - start_time
                    update_call_duration(
                        call_duration, event.from_user, duration)
                    # Remove call from ongoing_calls
                    ongoing_calls.remove((event.from_user, event.to_user))

                # Case where person hanging up is the callee
                start_time = call_start_times.get(event.to_user, None)
                if start_time is not None:
                    duration = event.timestamp - start_time
                    update_call_duration(
                        call_duration, event.to_user, duration)
                    # Remove call from ongoing_calls
                    ongoing_calls.remove((event.to_user, event.from_user))

            else:
                print(
                    f"Error: Hangup event encountered for {event.from_user} without a corresponding call.")

    result = []
    for caller, (total_duration, call_count) in call_duration.items():
        # Only consider users that have made calls
        avg_duration = total_duration / call_count if call_count > 0 else 0
        if avg_duration < 5:
            result.append(caller)
    print(call_duration)
    return result


if __name__ == "__main__":
    events = [
        Call("Bob", "Alice", 1711132463),
        Call("Carl", "Doug", 1711132465),
        Hangup("Alice", "Bob", 1711132467),
        Call("Ed", "Frank", 1711132481),
        Hangup("Carl", "Doug", 1711132482),
        Call("Bob", "Doug", 1711132483),
        Hangup("Doug", "Bob", 1711132484),
        Hangup("Ed", "Frank", 1711132501),
    ]

 # More test cases
    more_events = [
        # Multiple Calls with Short Durations
        Call("Bob", "Alice", 1),  # Bob calls Alice at time 1
        Hangup("Bob", "Alice", 2),  # Bob hangs up after 1 second
        Call("Bob", "Alice", 2),  # Bob calls Alice again at time 2
        Hangup("Bob", "Alice", 2),  # Bob hangs up immediately
        Call("Carl", "Doug", 3),  # Carl calls Doug at time 3
        Call("Ed", "Frank", 4),  # Ed calls Frank at time 4
        Hangup("Carl", "Doug", 5),  # Carl hangs up after 2 seconds
        Call("Carl", "Doug", 5),  # Carl calls Doug again at time 5
        Hangup("Carl", "Doug", 5),  # Carl hangs up immediately
        Call("Bob", "Doug", 6),  # Bob calls Doug at time 6
        Hangup("Ed", "Frank", 7),  # Ed hangs up after 3 seconds
        Hangup("Bob", "Doug", 10),  # Bob hangs up after 4 seconds


        # Multiple Calls with Same Duration
        Call("Bob", "Alice", 1),  # Bob calls Alice at time 1
        Call("Carl", "Doug", 2),  # Carl calls Doug at time 2
        Call("Ed", "Frank", 3),  # Ed calls Frank at time 3
        Hangup("Bob", "Alice", 6),  # Bob hangs up after 5 seconds
        Hangup("Carl", "Doug", 7),  # Carl hangs up after 5 seconds
        Hangup("Ed", "Frank", 8),  # Ed hangs up after 5 seconds
    ]

    edge_events = [
        # Calls hung up immediately
        Call("Bob", "Alice", 2),  # Bob calls Alice at time 2
        Hangup("Bob", "Alice", 2),  # Bob hangs up immediately
        Call("Carl", "Doug", 5),  # Carl calls Doug at time 5
        Hangup("Carl", "Doug", 5),  # Carl hangs up immediately

        # Calls made that are not hung up --> should not contribute to caller's call length
        Call("Greg", "Doug", 2),  # Greg calls Doug at time 2
        Call("Ed", "Frank", 3),  # Ed calls Frank at time 5

        # Hang up without call being made --> should error
        Hangup("Howie", "Ida", 2),

        # Hang up for a call to someone they have not made
        Call("Bob", "Alice", 4),
        Hangup("Bob", "Greg", 5),
        Hangup("Carl", "Doug", 6)
    ]


print("Original Events Result:", calculate_average_call_duration(events))
print("More Test Cases Result:", calculate_average_call_duration(more_events))
print("Edge Test Cases Result:", calculate_average_call_duration(edge_events))
