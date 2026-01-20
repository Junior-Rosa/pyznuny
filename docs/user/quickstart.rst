Quick Start
===========

On this page you will learn how to do some basic functions like creating a Ticket API client and creating some tickets
through it

Creating a Ticket client
------------------------

First import the pyznuny module and create a client object, informing the base URL, username and password. It is highly
recommended to use environment variables for these values, so we will be using
`dotenv <https://pypi.org/project/python-dotenv/>`_ for this

.. code-block:: python

    from pyznuny import TicketClient
    import os
    from dotenv import load_dotenv
    load_dotenv()

    client = TicketClient(base_url=os.getenv("HOST"),
                         username=os.getenv("USER_LOGIN"),
                         password=os.getenv("PASSWORD"))

In this example we have the environment variables set in a .env file like this:

.. code-block:: ini

    HOST=https://your-znuny-instance.com
    USER_LOGIN=your-username
    PASSWORD=your-password

Setting an endpoint
-------------------

Now that we have a client, we will create an endpoint, in our case we will do an endpoint for getting a ticket by its ID

To do this we will use the ``EndpointSetter`` class, which abstracts the process of setting an endpoint for common use cases

.. code-block:: python

    from pyznuny.ticket import EndpointSetter

    endpoint = EndpointSetter(client=client)
        .ticket_create("/ticket_create")

    print(endpoint)

Here we created an endpoint for creating tickets, pointing to the endpoint ``your-base-url/ticket-create/``

You can now check the endpoint created in your client with:

.. code-block:: python

    print(client.endpoints)


Creating a Ticket
-----------------

Now with an endpoint created for ticket creation, we can now send a ticket using the ``ticket`` attribute of the client
class. This attribute has common routes to interact with the API, like the ``create()`` function, which we will be using.
First we create a payload for the ticket creation

.. code-block:: python

    from pyznuny.ticket.models import TicketCreatePayload, TicketCreateTicket, TicketCreateArticle

    payload = TicketCreatePayload(
        Ticket=TicketCreateTicket(
            Title="Ticket Title",
            Queue="Ticket queue",
            State="Ticket state",
            Priority="Ticket priority",
        ),
        Article=TicketCreateArticle(
            Subject="Ticket subject",
            Body="Ticket body...",
            ContentType="text/plain; charset=utf-8",
        ),
    )

The payload consists of the ticket metadata and the article content

Now we just need to send the payload to the API

.. code-block:: python

    response = client.ticket.create(payload=payload)
    print("Create Ticket Response:", response.json())