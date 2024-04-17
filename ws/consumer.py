from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Book,Post,Comment,Review,BookRead
from user.models import Writer,Reader
from .serializers import books_serializer,authors_serializer,book_detail_serializer\
    ,posts_serializer,comments_serializer,reviews_serializer,stats_serializer,writer_detail_serializer,profile_serializer
import json
from .views import create_comment,like_content
from django.core.exceptions import ObjectDoesNotExist


class KitabConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def categories(self,data):
        status,content = await Book.filter.filter_by_category(data)
        if status:
            serialized_data = await books_serializer(content)
            return await self.send_massage(data['filter'],status,serialized_data)
        else:
            return await self.send_massage(data['filter'],status,content)

    async def author_categories(self,data):
        status,content = await Writer.filter.filter_by_category(data)
        if status:
            serialized_data = await authors_serializer(content)
            return await self.send_massage(data['filter'],status,serialized_data)
        else:
            return await self.send_massage(data['filter'],status,content)

    async def book_details(self,data):
        try:
            slug = data.get('slug',None)
            if slug:
                book = await Book.filter.get_details(slug)
                serialized_data = await book_detail_serializer(book)
                return await self.send_massage('book_details',True,serialized_data)
            else:
                return await self.send_massage('book_details',False,"bad request")
        except Exception as e:
            print(e)
            return await self.send_massage('book_details',False,"book not found")

    async def posts(self,data):
        try:
            status,content = await Post.filter.filter_by_category(data)
            if status:
                serialized_data = await posts_serializer(content)
                return await self.send_massage('book_posts',True,serialized_data)
            else:
                return await self.send_massage('book_posts',status,content)
        except Exception as e:
            print(e)
            return await self.send_massage('book_posts',False,"book not found")

    async def create_post(self,data):
        user = self.scope['user']
        if user.is_authenticated:
            slug,post,page = data.get('slug',None),data.get('post',None),data.get('page',None)
            if slug and post and page:
                try:
                    reader = await Reader.objects.aget(user = user)
                    book = await Book.objects.aget(slug = slug)
                    await Post.objects.acreate(user = reader,book = book,context= post,page_num = page)
                    return await self.send_massage('create_post',True,"created")
                except ObjectDoesNotExist:
                    return await self.send_massage('create_post',False,"book not found")
            else:
                return await self.send_massage('create_post',False,"data is incomplate")
        else:
            return await self.send_massage('create_post',False,"user not verified")
 
    async def create_review(self,data):
        user = self.scope['user']
        if user.is_authenticated:
            slug,context,page,rate,title = data.get('slug',None),data.get('context',None),data.get('page_num',None),data.get('rate',None),data.get('title',None)
            if slug and context and page and rate and title:
                if rate > 10 or rate < 0:
                    return await self.send_massage('create_post',False,"rate must be between 0-10") 
                try:
                    reader = await Reader.objects.aget(user = user)
                    book = await Book.objects.aget(slug = slug)
                    await Review.objects.acreate(user = reader,book = book,context= context,page_num = page,title = title,rate = rate)
                    return await self.send_massage('create_post',True,"created")
                except ObjectDoesNotExist:
                    return await self.send_massage('create_post',False,"book not found")
            else:
                return await self.send_massage('create_post',False,"data is incomplate")
        else:
            return await self.send_massage('create_post',False,"user not verified")
        
    async def create_comment(self,data):
        {
            "action":"create_comment",
            "type":"post", #post review
            "id":1,
            "comment":"data"
        }
        user = self.scope['user']
        if user.is_authenticated:
            status,context = await create_comment(data,user)
            return await self.send_massage('create_comment',status,context)
        else:
            return await self.send_massage('create_post',False,"user not verified")

    async def get_comment(self,data):
        {
            "action":"get_comment",
            "type":"post", #post #review
            "id":1,
        }
        comments = await Comment.filter.filter_comments(data)
        serialized_data = await comments_serializer(comments)
        return await self.send_massage('get_comment',True,serialized_data)

    async def get_review(self,data):
        {
            "action":"get_review",
            "type":"book", #writer
            "filter":"new_review",# new_review old_review high_rate low_rate popular
            "id":1
        }
        context = dict()
        if data['type'] == "book":
            overal,stats = await Book.filter.get_stats(data['id'])
            if not overal:
                return await self.send_massage('get_review',False,'book not found')

            stast_data = await stats_serializer(stats,overal)
            context['overal']=stast_data

        status,reviews = await Review.filter.filter_reviews(data)
        if not status:
            return await self.send_massage('get_review',status,reviews)
        reviews_data = await reviews_serializer(reviews)
        context['reviews']=reviews_data
            
        return await self.send_massage('get_review',True,context)

    async def like(self,data):
        {
            "action":"like",
            "type":"post", # post, review, comment
            "id":1,
        }
        user = self.scope['user']
        if user.is_authenticated:   
            status,context = await like_content(data,user)
            return await self.send_massage("like",status,context)
        else:
            return await self.send_massage('create_post',False,"user not verified")
        
    async def writer_details(self,data):
        id = data.get('id',None)
        if id:
            try:
                writer = await Writer.filter.get_details(id)
                serialized_data = await writer_detail_serializer(writer)
                return await self.send_massage('writer_details',True,serialized_data)
            except ObjectDoesNotExist:
                return await self.send_massage('writer_details',False,'writer not found')
        else:
            return await self.send_massage('writer_details',False,"bad request")
    
    async def writer_books(self,data):
        {
            "action":"writer_books",
            "filter":"the_best",#most_read most_view
            "id":1
        }

        try:
            writer = await Writer.objects.aget(id = data['id'])
            status,books = await Book.filter.filter_by_category(data,writer)
            if status:
                serialized_data = await books_serializer(books)
                return await self.send_massage('writer_books',True,serialized_data)
            else:
                return await self.send_massage('writer_books',False,books)
        except ObjectDoesNotExist:
            return await self.send_massage('writer_books',False,"writer not found")

    async def book_readers(self,data):

        slug,status = data.get('slug',None),data.get('status',None)
        if slug and status:
            readers = await BookRead.filter.filter_users_by_status(slug,status)
            serialized_data = await profile_serializer(readers)
            return await self.send_massage('book_readers',True,serialized_data)
        else:
            return await self.send_massage('create_post',False,"data is incomplate")

    actions = {
        'categories':categories,
        'author_categories':author_categories,
        'book_details':book_details,
        'posts':posts,
        'create_post':create_post,
        'create_review':create_review,
        'create_comment':create_comment,
        'get_comment':get_comment,
        'get_review':get_review,
        'like':like,
        'writer_details':writer_details,
        'writer_books':writer_books,
        'book_readers':book_readers,
    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        if self.actions.get(data.get('action',None),None):
            await self.actions[data['action']](self, data)
        else:
            return await self.send_massage('error',False,'action not found')

    async def send_massage(self,action,status, message):
        await self.send(text_data=json.dumps(
                {
                    'status':status,
                    'action':action,
                    'message':message,
                }
            ))
