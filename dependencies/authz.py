from dependencies.authn import authenticated_user
from fastapi import Depends, HTTPException, status
from typing import Annotated, Any

permission = [
     {
          "role": "admin",
          "permission": ["post_event", "get_events", "get_event", "put_event", "delete_event", "delete_user", "put_user"]
     },
     {
          "role": "host",
          "permission": ["post_event", "get_events", "get_event", "put_event", "delete_event"]
     },
     {
          "role": "guest",
          "permission": ["get_events", "get_event"]
     }
]


def has_roles(roles):
    def check_roles(
            user: Annotated[Any, Depends(authenticated_user)]):
            if not user["role"] in roles:
                raise HTTPException(
                     status.HTTP_403_FORBIDDEN,
                     detail="Access denied!"           
    )
    return check_roles 