from django.utils import timezone
from .models import  Species, Publisher, Book,Post,Comment,Review,Like
from user.models import Writer,Role,Reader
from django.core.exceptions import ObjectDoesNotExist

async def create_comment(data: dict,user):
    comment_types = {
        'post': Post,
        'review': Review
    }

    try:
        user = await Reader.objects.aget(user = user)
        
        comment_type = data.get('type')
        comment_id = data.get('id')
        comment_text = data.get('comment')

        if not comment_type or not comment_id or not comment_text:
            return False,"Missing required data"

        if comment_type not in comment_types:
            return False,"Invalid comment type"

        comment_model = comment_types[comment_type]
        
        comment_object = await comment_model.objects.aget(id=comment_id)

        await Comment.objects.acreate(
            type=comment_type,
            **{comment_type: comment_object},
            user=user,
            text=comment_text
        )
        return True, "Created"
    
    except ObjectDoesNotExist:
        return False ,f"No {comment_type} found with id={comment_id}",

async def like_content(data,user):
    comment_types = {
        'post': Post,
        'review': Review,
        'comment': Comment,
    }

    try:
        user = await Reader.objects.aget(user = user)
        comment_type = data.get('type')
        comment_id = data.get('id')

        if not comment_type or not comment_id:
            return False,"Missing required data"

        if comment_type not in comment_types:
            return False,"Invalid comment type"

        comment_model = comment_types[comment_type]
        
        comment_object = await comment_model.objects.aget(id=comment_id)

        await Like.objects.aget_or_create(
            type=comment_type,
            **{comment_type: comment_object},
            user=user,
        )
        return True, "Created"
    
    except ObjectDoesNotExist:
        return False ,f"No {comment_type} found with id={comment_id}",








def populate(request):

    # Assuming you have a list of writers with their books
    writers_data = [
        {
            'first_name': 'Stephen',
            'last_name': 'King',
            'books': [
                {'name': 'The Shining', 'publication_date': '2019-01-28'},
                {'name': 'It', 'publication_date': '2023-09-15'}
            ]
        },
        {
            'first_name': 'J.K.',
            'last_name': 'Rowling',
            'books': [
                {'name': 'Harry Potter and the Philosopher\'s Stone', 'publication_date': '2023-06-26'},
                {'name': 'Harry Potter and the Chamber of Secrets', 'publication_date': '2019-07-02'}
            ]
        },
        {
            'first_name': 'Harper',
            'last_name': 'Lee',
            'books': [
                {'name': 'To Kill a Mockingbird', 'publication_date': '2023-07-11'}
            ]
        },
        {
            'first_name': 'Tolkien',
            'last_name': 'J.R.R.',
            'books': [
                {'name': 'The Hobbit', 'publication_date': '2019-09-21'},
                {'name': 'The Lord of the Rings', 'publication_date': '2023-07-29'}
            ]
        },
        {
            'first_name': 'Mark',
            'last_name': 'Twain',
            'books': [
                {'name': 'The Adventures of Tom Sawyer', 'publication_date': '2023-12-01'},
                {'name': 'Adventures of Huckleberry Finn', 'publication_date': '2023-12-10'}
            ]
        },
        {
            'first_name': 'Virginia',
            'last_name': 'Woolf',
            'books': [
                {'name': 'Mrs. Dalloway', 'publication_date': '2023-05-14'},
                {'name': 'To the Lighthouse', 'publication_date': '2023-05-05'}
            ]
        },
        {
            'first_name': 'George',
            'last_name': 'Orwell',
            'books': [
                {'name': '1984', 'publication_date': '2023-06-08'},
                {'name': 'Animal Farm', 'publication_date': '2019-08-17'}
            ]
        },
        {
            'first_name': 'Agatha',
            'last_name': 'Christie',
            'books': [
                {'name': 'Murder on the Orient Express', 'publication_date': '2023-01-01'},
                {'name': 'The Murder of Roger Ackroyd', 'publication_date': '2019-06-01'}
            ]
        },
        {
            'first_name': 'Ernest',
            'last_name': 'Hemingway',
            'books': [
                {'name': 'The Old Man and the Sea', 'publication_date': '2023-09-01'},
                {'name': 'A Farewell to Arms', 'publication_date': '2019-09-27'}
            ]
        },
        {
            'first_name': 'Jane',
            'last_name': 'Austen',
            'books': [
                {'name': 'Pride and Prejudice', 'publication_date': '2023-01-28'},
                {'name': 'Sense and Sensibility', 'publication_date': '2019-10-30'}
            ]
        },
    ]

    # Create roles
    writer_role = Role.objects.get_or_create(role='Writer')[0]

    # Create species
    novel_species = Species.objects.get_or_create(name='Novel')[0]

    # Create publishers
    publisher = Publisher.objects.get_or_create(name='Random House')[0]

    # Create writers with their books
    for writer_data in writers_data:
        writer = Writer.objects.create(
            first_name=writer_data['first_name'],
            last_name=writer_data['last_name'],
            bio=f'Biography of {writer_data["first_name"]} {writer_data["last_name"]}',
            title='Author',
            birth_date=timezone.now(),
            death_date=timezone.now(),
        )
        writer.role.add(writer_role)
        
        for book_data in writer_data['books']:
            book = Book.objects.create(
                writer=writer,
                publisher=publisher,
                publication_date=book_data['publication_date'],
                release_date=book_data['publication_date'],
                num_pages=300,
                name=book_data['name'],
                reading_time='2 hours',
                original_name=book_data['name'],
                isbn='1234567890',
                country='USA',
                language='English',
                format='Hardcover',
                about=f'About {book_data["name"]}',
            )
            book.species.add(novel_species)
