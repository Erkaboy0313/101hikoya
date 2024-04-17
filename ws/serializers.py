from .models import Book,Post,Comment,BookRead
from user.models import Writer
from .utils import format_time_difference

async def book_serializer(book:Book):
    return {
            'id':book.id,
            'slug':book.slug,
            'name':book.name,
            'image_url':await book.imageURL,
            'writer':await book.writer.full_name,
            'date':book.release_date.strftime("%B %Y"),
            'rate':round(book.sum_rate / book.count_rate,1) if book.count_rate else 0,
            'read_count':book.read_count if hasattr(book,'read_count') else None,
            'last_post':book.last_post if hasattr(book,'last_post') else None,
            'like_count':book.like_count if hasattr(book,'like_count') else None,
            'view_count':book.view_count if hasattr(book,'view_count') else None,
            'will_read_count':book.will_read_count if hasattr(book,'will_read_count') else None,
            'quote_count':book.quote_count if hasattr(book,'quote_count') else None,
            'abandoned_count':book.abandoned_count if hasattr(book,'abandoned_count') else None,
            'review_count':book.review_count if hasattr(book,'review_count') else None,
            'reading_count':book.reading_count if hasattr(book,'reading_count') else None,
        }   

async def books_serializer(books):
    serialized_data = [await book_serializer(x) async for x in books]
    return serialized_data

async def author_serializer(author:Writer):
    return {
        'id':author.id,
        'name':await author.full_name,
        'image_url':await author.imageURL,
        'rate':round(author.sum_rate / author.count_rate,1) if author.count_rate else 0,
        'read_count':author.read_count if hasattr(author,'read_count') else None,
        'last_post':author.last_post if hasattr(author,'last_post') else None,
        'like_count':author.like_count if hasattr(author,'like_count') else None,
        'view_count':author.view_count if hasattr(author,'view_count') else None,
        'quote_count':author.quote_count if hasattr(author,'quote_count') else None,
        'book_count':author.book_count if hasattr(author,'book_count') else None,
        'review_count':author.review_count if hasattr(author,'review_count') else None,
        }   

async def authors_serializer(authors):
    serialized_data = [await author_serializer(x) async for x in authors]
    return serialized_data

async def book_detail_serializer(book:Book):

    other_prints = await Book.filter.other_prints(book)
    author_books = await Book.filter.author_books(book)
    similar_books = await Book.filter.similar_books(book)
    stats = await Book.filter.get_statistics(book.slug)

    for key,value in stats.items():
        if not key == 'all':
            print(key,value)
            stats[key] = round((100 / stats['all']) * value,1) if stats['all'] else 0

    book_info = await book_serializer(book)
    book_info['writer'] = {
        'name':await book.writer.full_name,
        'bio':book.writer.bio,
        'image':await book.writer.imageURL
    }
    book_details = {
        'translator':book.translator.full_name if book.translator else None,
        'species':",".join([x.name for x in book.species.all()]),
        'num_pages':book.num_pages,
        'reading_time':book.reading_time,
        'original_name':book.original_name,
        'isbn':book.isbn,
        'country':book.country,
        'language':book.language,
        'format':book.format,
        'about':book.about,
        'author_book_count':await author_books.acount(),
        'stats':stats,
        'other_prints':[await book_serializer(x) async for x in other_prints],
        'author_books':[await book_serializer(x) async for x in author_books],
        'similar_books':[await book_serializer(x) async for x in similar_books],
    }
    return {**book_info,**book_details}

async def post_serializer(post:Post):

    post_user = {
        'image':await post.user.imageURL,
        'fullname':await post.user.full_name
    }

    post_book = {
        'name':post.book.name,
        'image':await post.book.imageURL,
        'author':await post.book.writer.full_name
    }

    post = {
        "id":post.id, 
        "page_num":post.page_num,
        "context":post.context,
        "time":await format_time_difference(post.time),
        "like":post.like_count,
        "share":post.share_count,
        "comment":post.comment_count,
        "post_user":post_user,
        "post_book":post_book
    }
    return post

async def posts_serializer(posts):
    return [await post_serializer(x) async for x in posts]

async def comment_serializer(comment:Comment):
    return  {
            "user":{
                'image':await comment.user.imageURL,
                'fullname':await comment.user.full_name
            },
            "like":comment.like_count,
            "text":comment.text
        }

async def comments_serializer(comments):
    return [await comment_serializer(x) async for x in comments]

async def review_serializer(review):
    read_status = await BookRead.objects.filter(user = review.user, book = review.book).afirst()
    review_user = {
            'image':await review.user.imageURL,
            'fullname':await review.user.full_name,
            'read_status':read_status.status if read_status else None,
        }
    review_book = {
        'name':review.book.name,
        'name':review.book.num_pages,
        'image':await review.book.imageURL,
        'author':await review.book.writer.full_name
    }
    data = {
        "user":review_user,
        "book":review_book,
        "rate":review.rate,
        "title":review.title,
        "context":review.context,
        "like_count":review.like_count,
        "share_count":review.share_count,
        "comment_count":review.comment_count,
    }
    return data

async def stats_serializer(stats,overals):
    res = dict()
    async for x in stats:
        if x['rate_group'] and overals['rated_review']:
            res[x['rate_group']] = round((100 / overals['rated_review']) * x['rate_group_count'],1)
    
    for i in range(1,6):
        if i not in res:
            res[i] = 0
    overals['rate'] = round(overals['rate'],1) if overals['rate'] else None
    return {**res,**overals}

async def reviews_serializer(reviews):
    return [await review_serializer(x) async for x in reviews]

async def profile_serializer(readers):
    result = []
    async for x in readers:
        data = {
            "image":await x.user.imageURL,
            "name":await x.user.full_name,
            "total_reads":x.user_total_read,
        }
        result.append(data)
    return result

async def writer_detail_serializer(writer:Writer):
    writer_info = await author_serializer(writer)
    writer_details = {
        "reading_count":writer.reading_count,
        "will_read_count":writer.will_read_count,
        "abandoned_count":writer.abandoned_count,
        "about":writer.bio,
        "title":writer.title,
        "birth":writer.birth_date.strftime("%d-%m-%Y"),
        "death":writer.death_date.strftime("%d-%m-%Y"),
        "books":[await book_serializer(x) async for x in await Book.filter.get_author_books(writer)],
    }
    return {**writer_info,**writer_details}