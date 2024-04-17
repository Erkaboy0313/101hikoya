from django.db.models import Sum,Count,Q,Min
from django.db.models.query import QuerySet
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def exist_user(self, data):
        queryset = get_user_model().objects
        if data.get('user_id', None):
            queryset = queryset.filter(~Q(id=data.get('user_id')))
        return queryset.filter(
            Q(email=data['email']) |
            Q(phone=data['phone']) |
            Q(username=data['username']) 
        ).exists()

    def create_user(self, role, email, phone, password=None, *args, **kwargs):
        return get_user_model().objects.create(
            email=email,
            phone=phone,
            role=role,
            password=make_password(password),
            *args,
            **kwargs
        )

    def create_superuser(self, email, password, *args, **kwargs):
        return get_user_model().objects.create(
            role=self.model.UserRole.ADMIN,
            email=email,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            *args,
            **kwargs
        )

class ReaderManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.UserRole.READER)

class AdminManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.UserRole.ADMIN)



class WriterManager(BaseUserManager):

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().prefetch_related('writer')\
            .annotate(sum_rate=Sum('writer__review__rate',filter=Q(writer__review__rate__gt = 0)),
                      count_rate = Count('writer__review',filter=Q(writer__review__rate__gt = 0)))
    
    async def new_popular(self):
        last_year = timezone.now().year - 1
        return self.annotate(first_book_release_date=Min('writer__release_date'))\
            .filter(first_book_release_date__year=last_year)\
                .annotate(read_count=Count('writer__bookread', filter=Q(writer__bookread__status='read'),distinct=True)).order_by('-read_count')

    async def popular_2023(self):
        return self.annotate(first_book_release_date=Min('writer__release_date'))\
            .filter(first_book_release_date__year=2023)\
                .annotate(read_count=Count('writer__bookread', filter=Q(writer__bookread__status='read'),distinct=True)).order_by('-read_count')
    
    async def most_post_in_last_24(self):
        now = timezone.now()
        last_24_hours = now - timedelta(hours=24)
        return self.annotate(last_post=Count('post', filter=Q(post__time__range=[last_24_hours, now]),distinct=True)).order_by('-last_post')

    async def most_read_last_5(self):
        last_5_year = timezone.now().year - 5
        return self.annotate(first_book_release_date=Min('writer__release_date'))\
            .filter(first_book_release_date__year__gte=last_5_year)\
                .annotate(read_count=Count('writer__bookread', filter=Q(writer__bookread__status='read'),distinct=True)).order_by('-read_count')
    
    async def the_best(self):
        return self.order_by('-rate')
    
    async def most_read(self):
        return self.annotate(read_count=Count('writer__bookread', filter=Q(writer__bookread__status='read'),distinct=True)).order_by('-read_count')
    
    async def most_likes(self):
        return self.annotate(like_count=Count('like',distinct=True)).order_by('-like')
    
    async def most_view(self):
        return self.annotate(view_count=Count('view',distinct=True)).order_by('-view_count')
    
    async def most_quote(self):
        return self.annotate(quote_count=Count('quote',distinct=True)).order_by('-quote_count')
    
    async def most_review(self):
        return self.annotate(review_count=Count('review',distinct=True)).order_by('-review_count')
    
    async def most_book(self):
        return self.annotate(book_count=Count('writer',distinct=True)).order_by('-book_count')

    async def filter_by_category(self,data:dict):
        categories = {
            'new_popular':self.new_popular,
            'popular_2023':self.popular_2023,
            'most_post_in_last_24':self.most_post_in_last_24,
            'most_read_last_5':self.most_read_last_5,
            'the_best':self.the_best,
            'most_read':self.most_read,
            'most_likes':self.most_likes,
            'most_view':self.most_view,
            'most_quote':self.most_quote,
            'most_review':self.most_review,
            'most_book':self.most_book,
        }
        category = categories.get(data.get('filter',None),None)
        if category:
            return(True, await category())
        else:
            return (False, 'wrong category')
    
    async def get_details(self,id):
        return await self.annotate(
            like_count=Count('like',distinct=True),
            view_count=Count('view',distinct=True),
            read_count = Count('writer__bookread', filter=Q(writer__bookread__status = 'read'),distinct=True),
            reading_count = Count('writer__bookread', filter=Q(writer__bookread__status = 'reading'),distinct=True),
            will_read_count = Count('writer__bookread', filter=Q(writer__bookread__status = 'will read'),distinct=True),
            abandoned_count = Count('writer__bookread', filter=Q(writer__bookread__status = 'abandoned'),distinct=True)
        ).aget(id = id)

