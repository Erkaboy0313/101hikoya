from django.db.models import Manager,Avg,Count,Q,Case,When,IntegerField,Sum,FloatField
from django.db.models.query import QuerySet
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Cast


class BookManager(Manager):

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related('writer')\
            .annotate(sum_rate=Sum('review__rate',filter=Q(review__rate__gt = 0)),count_rate= Count('review',filter=Q(review__rate__gt = 0))\
                      ,read_count = Count('bookread', filter=Q(bookread__status = 'read'),distinct=True))

    async def new_releases(self):
        return self.order_by('-release_date')
    
    async def new_popular(self):
        last_year = timezone.now().year - 1
        return self.filter(release_date__year__gte = last_year).order_by('-read_count')
    
    async def popular_in_2023(self):
        return self.filter(release_date__year = 2023).order_by('-read_count')
    
    async def most_post_in_last_24(self):
        now = timezone.now()
        last_24_hours = now - timedelta(hours=24)
        return self.annotate(last_post=Count('post',filter=Q(post__time__range=[last_24_hours, now]),distinct=True)).order_by('-last_post')
       
    async def most_read_last_5(self):
        last_5_year = timezone.now().year - 5
        return self.filter(release_date__year__gte = last_5_year).order_by('-read_count')
    
    async def the_best(self,writer=None):
        if writer:
            return self.filter(writer = writer).order_by('-rate')
        return self.order_by('-rate')
    
    async def most_likes(self):
        return self.annotate(like_count=Count('like',distinct=True)).order_by('-like')
    
    async def most_read(self,writer=None):
        if writer:
            return self.filter(writer = writer).order_by('-read_count')
        return self.order_by('-read_count')
    
    async def most_view(self,writer=None):
        if writer:
            return self.filter(writer = writer).annotate(view_count=Count('view',distinct=True)).order_by('-view_count')
        return self.annotate(view_count=Count('view',distinct=True)).order_by('-view_count')
    
    async def most_will_read(self):
        return self.annotate(will_read_count = Count('bookread', filter=Q(bookread__status = 'will read'),distinct=True)).order_by('-will_read_count')
    
    async def most_quote(self):
        return self.annotate(quote_count=Count('quote',distinct=True)).order_by('-quote_count')
    
    async def most_review(self):
        return self.annotate(review_count=Count('review',distinct=True)).order_by('-review_count')

    async def most_abandoned(self):
        return self.annotate(abandoned_count = Count('bookread', filter=Q(bookread__status = 'abandoned'),distinct=True)).order_by('-abandoned_count')

    async def get_statistics(self,slug):
        return await self.prefetch_related('bookread__user').filter(slug = slug).aaggregate(
            first = Count("bookread",filter=Q(bookread__user__age__range = (1,12))),
            secont = Count("bookread",filter=Q(bookread__user__age__range = (13,24))),
            third = Count("bookread",filter=Q(bookread__user__age__range = (24,40))),
            fourth = Count("bookread",filter=Q(bookread__user__age__gt = 40)),
            male = Count("bookread",filter=Q(bookread__user__gender = 'male')),
            femele = Count("bookread",filter=Q(bookread__user__gender = 'female')),
            all = Count("bookread",filter=Q(bookread__status = 'read'),distinct=True)
        )


    async def get_details(self,slug):
        return await self.select_related('writer','translator','publisher').prefetch_related('species').annotate(
            like_count=Count('like',distinct=True),
            view_count=Count('view',distinct=True),
            quote_count=Count('quote',distinct=True),
            review_count=Count('review',distinct=True),
            reading_count = Count('bookread', filter=Q(bookread__status = 'reading'),distinct=True),
            will_read_count = Count('bookread', filter=Q(bookread__status = 'will read'),distinct=True),
            abandoned_count = Count('bookread', filter=Q(bookread__status = 'abandoned'),distinct=True)
        ).aget(slug = slug)

    async def filter_by_category(self,data:dict,writer=None):
        categories = {
            'new_releases':self.new_releases,
            'new_popular':self.new_popular,
            'popular_in_2023':self.popular_in_2023,
            'most_post_in_last_24':self.most_post_in_last_24,
            'most_read_last_5':self.most_read_last_5,
            'the_best':self.the_best,
            'most_likes':self.most_likes,
            'most_read':self.most_read,
            'most_view':self.most_view,
            'most_will_read':self.most_will_read,
            'most_quote':self.most_quote,
            'most_abandoned':self.most_abandoned,
            'most_review':self.most_review,
        }
        category = categories.get(data.get('filter',None),None)
        if category:
            if writer:
                return(True, await category(writer))
            return(True, await category())
        else:
            return (False, 'wrong category')

    async def other_prints(self,book):
        return self.filter(name = book.name).exclude(publisher = book.publisher)
    
    async def author_books(self,book):
        return self.filter(writer = book.writer)
    
    async def similar_books(self,book):
        return self.filter(species__in = book.species.all()).exclude(slug = book.slug)
    
    async def get_stats(self,id):
        if await self.filter(id = id).aexists():
            stats = self.filter(id = id).annotate(rate_group = Case(
                When(review__rate__range = (1,2),then=1),
                When(review__rate__range = (3,4),then=2),
                When(review__rate__range = (5,6),then=3),
                When(review__rate__range = (7,8),then=4),
                When(review__rate__range = (9,10),then=5),
                output_field=IntegerField()
            )).annotate(
                rate_group_count=Count('rate_group'),
            ).values('rate_group','rate_group_count')

            overals = await self.filter(id = id).aaggregate(
                tottal_review=Count('review',distinct=True),
                rated_review=Count('review',filter=Q(review__rate__gt = 0),distinct=True),
                rate=Avg('review__rate',filter=Q(review__rate__gt = 0),distinct=True)
                )
            return overals,stats
        else:
            return False,False

    async def get_author_books(self,writer):
        return self.filter(writer = writer)

class PostManager(Manager):

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related('user','book','writer','book__writer').annotate(
            like_count = Count('like',distinct=True),
            share_count = Count('share',distinct=True),
            comment_count = Count('comment',distinct=True),
        )

    async def get_new_book_posts(self,slug,writer):
        if writer:
            return self.filter(book__writer__id = writer).order_by('-time')
        else:    
            return self.filter(book__slug = slug).order_by('-time')
    
    async def get_high_book_posts(self,slug,writer):
        if writer:
            return self.filter(book__writer__id = writer).order_by('-share_count')
        else:    
            return self.filter(book__slug = slug).order_by('-share_count')
    
    async def get_liked_book_posts(self,slug,writer):
        if writer:
            return self.filter(book__writer__id = writer).order_by('-like_count')
        else:    
            return self.filter(book__slug = slug).order_by('-like_count')
    
    async def get_old_book_posts(self,slug,writer):
        if writer:
            return self.filter(book__writer__id = writer).order_by('time')
        else:    
            return self.filter(book__slug = slug).order_by('time')

    async def filter_by_category(self,data:dict):
        categories = {
            'new_posts':self.get_new_book_posts,
            'highlights':self.get_high_book_posts,
            'most_liked':self.get_liked_book_posts,
            'old_posts':self.get_old_book_posts,
        }
        category = categories.get(data.get('filter',None),None)
        slug = data.get('slug',None)
        writer = data.get('writer',None)
        if category and (slug or writer):
            return(True, await category(slug,writer))
        elif not category:
            return (False, 'wrong category')
        elif not slug:
            return (False, 'bad request')
        
class CommentManager(Manager):
    
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related('user').annotate(like_count = Count('like',distinct=True))
    
    async def filter_comments(self,data):
        type = data.get('type')
        id = data.get('id')

        if type == 'post':
            return self.filter(post__id = id)

        if type == 'review':
            return self.filter(review__id = id)

class ReviewManager(Manager):

    def get_queryset(self,type,id) -> QuerySet:
        if type == 'book':
            return super().get_queryset().filter(book_id = id).select_related('user',"book",'book__writer').annotate(
                like_count = Count('like',distinct=True),
                share_count = Count('share',distinct=True),
                comment_count = Count('comment',distinct=True),
                )
        elif type == 'writer':
            return super().get_queryset().filter(book__writer__id = id).select_related('user',"book",'book__writer').annotate(
                like_count = Count('like',distinct=True),
                share_count = Count('share',distinct=True),
                comment_count = Count('comment',distinct=True),
                )
    
    async def new_review(self,type,id):
        return self.get_queryset(type,id).order_by('time')
    
    async def old_review(self,type,id):
        return self.get_queryset(type,id).order_by('-time')

    async def high_rate(self,type,id):
        return self.get_queryset(type,id).order_by('-comment_count')

    async def low_rate(self,type,id):
        return self.get_queryset(type,id).order_by('comment_count')

    async def popular(self,type,id):
        return self.get_queryset(type,id).order_by('-like_count')

    async def filter_reviews(self,data):
        type = data.get('type')
        id = data.get('id')

        categories = {
            'new_review':self.new_review,
            'old_review':self.old_review,
            'high_rate':self.high_rate,
            'low_rate':self.low_rate,
            'popular':self.popular,
        }

        category = categories.get(data.get('filter',None),None)

        if category:
            return(True, await category(type,id))
        
        if not category:    
            return (False, 'wrong category')

class BookReadManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'book')

    async def filter_users_by_status(self, slug, status):
        return self.filter(book__slug=slug, status=status).annotate(user_total_read=Count('user__bookread',filter=Q(user__bookread__status = 'read')))

