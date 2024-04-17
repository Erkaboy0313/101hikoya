from django.db import models
from .managers import BookManager,PostManager,CommentManager,ReviewManager,BookReadManager
from django.utils.text import slugify
from random import randint
    
class Species(models.Model):
    name = models.CharField(max_length = 150)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length = 150)

    def __str__(self):
        return self.name

class Book(models.Model):
    slug = models.SlugField(max_length = 50,blank=True,unique = True)
    writer = models.ForeignKey("user.Writer",related_name = 'writer',on_delete=models.SET_NULL,null = True)
    translator = models.ForeignKey("user.Writer",related_name = 'translator',on_delete=models.SET_NULL,null = True)
    publisher = models.ForeignKey(Publisher,on_delete = models.SET_NULL,null = True)
    species = models.ManyToManyField(Species,blank=True)
    image = models.ImageField(upload_to='book/',blank=True,null=True)
    num_pages = models.IntegerField()
    publication_date = models.DateField()
    release_date = models.DateField()
    name = models.CharField(max_length = 150)
    reading_time = models.CharField(max_length = 150)
    original_name = models.CharField(max_length = 150)
    isbn = models.CharField(max_length = 150)
    country = models.CharField(max_length = 150)
    language = models.CharField(max_length = 150)
    format = models.CharField(max_length = 150)
    about = models.TextField()
    views = models.IntegerField(default = 0)

    objects = models.Manager()
    filter = BookManager()

    @property
    async def imageURL(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(f"{self.name}--{randint(100000,999999)}") 
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} | {self.publisher}"


class Review(models.Model):
    user = models.ForeignKey("user.Reader", on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE,blank=True, null=True)
    page_num = models.IntegerField(blank=True, null=True)
    rate = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length = 150)
    context = models.TextField()
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    objects = models.Manager()
    filter = ReviewManager()

    def __str__(self):
        return f"{self.book} - {self.rate}"
    
class Post(models.Model):
    user = models.ForeignKey("user.Reader", on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE,blank=True, null=True)
    page_num = models.IntegerField(blank=True, null=True)
    context = models.TextField()
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    objects = models.Manager()
    filter = PostManager()

    def __str__(self):
        return f"{self.user} | {self.book}"

class Quote(models.Model):
    user = models.ForeignKey("user.Reader", on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE,blank=True, null=True)
    page_num = models.IntegerField(blank=True, null=True)
    quote = models.CharField(max_length = 150)
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    def __str__(self):
        return f"{self.user} | {self.quote}"

class Message(models.Model):
    user = models.ForeignKey("user.Reader", on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE,blank=True, null=True)
    writer = models.ForeignKey("user.Writer", on_delete = models.CASCADE,blank=True, null=True)
    message = models.CharField(max_length = 150)
    image = models.ImageField(upload_to='Messages/')
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    def __str__(self):
        return self.message

class BookRead(models.Model):
    
    class Status(models.TextChoices):
        WILL_READ = 'will read'
        READING = 'reading'
        READ = 'read'
        ABANDONED = 'abandoned'

    user = models.ForeignKey("user.Reader", on_delete = models.SET_NULL,null=True)
    book = models.ForeignKey(Book, on_delete = models.SET_NULL,null=True)
    status = models.CharField(max_length = 12,choices = Status.choices)
    started_time = models.DateField(blank=True, null=True)
    finished_time = models.DateField(blank=True, null=True)

    filter = BookReadManager()

    def __str__(self):
        return f"{self.user} | {self.book}"


class ExtraContentType(models.TextChoices):
    REVIEW = 'review'
    QUOTE = 'quote'
    POST = 'post'
    MESSAGE = 'message'
    COMMENT = 'comment'
    WRITER = 'writer'
    BOOK = 'book'

class Comment(models.Model):
    type = models.CharField(max_length = 10,choices = ExtraContentType.choices)

    post = models.ForeignKey(Post,on_delete = models.CASCADE,blank=True, null=True)
    message = models.ForeignKey(Message,on_delete = models.CASCADE,blank=True, null=True)
    quote = models.ForeignKey(Quote,on_delete = models.CASCADE,blank=True, null=True)
    review = models.ForeignKey(Review,on_delete = models.CASCADE,blank=True, null=True)

    user = models.ForeignKey("user.Reader",on_delete = models.SET_NULL,null=True)
    text = models.TextField(blank=True, null=True)
    
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    reply = models.ForeignKey('self',on_delete= models.CASCADE,blank=True, null=True)


    objects = models.Manager()
    filter = CommentManager()

    def __str__(self):
        return self.type

class Like(models.Model):    
    type = models.CharField(max_length = 10,choices = ExtraContentType.choices)

    message = models.ForeignKey(Message,on_delete = models.CASCADE,blank=True, null=True)
    post = models.ForeignKey(Post,on_delete = models.CASCADE,blank=True, null=True)
    quote = models.ForeignKey(Quote,on_delete = models.CASCADE,blank=True, null=True)
    review = models.ForeignKey(Review,on_delete = models.CASCADE,blank=True, null=True)
    comment = models.ForeignKey(Comment,on_delete = models.CASCADE,blank=True, null=True)
    book = models.ForeignKey(Book,on_delete = models.CASCADE,blank=True, null=True)
    
    writer = models.ForeignKey("user.Writer",on_delete = models.CASCADE,blank=True, null=True)
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    user = models.ForeignKey("user.Reader",on_delete = models.SET_NULL,null=True)

class View(models.Model):    
    type = models.CharField(max_length = 10,choices = ExtraContentType.choices)

    post = models.ForeignKey(Post,on_delete = models.CASCADE,blank=True, null=True)
    book = models.ForeignKey(Book,on_delete = models.CASCADE,blank=True, null=True)
    writer = models.ForeignKey("user.Writer",on_delete = models.CASCADE,blank=True, null=True)
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    user = models.ForeignKey("user.Reader",on_delete = models.SET_NULL,null=True)



class Share(models.Model):
    type = models.CharField(max_length = 10,choices = ExtraContentType.choices)

    post = models.ForeignKey(Post,on_delete = models.CASCADE,blank=True, null=True)
    message = models.ForeignKey(Message,on_delete = models.CASCADE,blank=True, null=True)
    quote = models.ForeignKey(Quote,on_delete = models.CASCADE,blank=True, null=True)
    review = models.ForeignKey(Review,on_delete = models.CASCADE,blank=True, null=True)
    comment = models.ForeignKey(Comment,on_delete = models.CASCADE,blank=True, null=True)
    time = models.DateTimeField(auto_now_add = True, blank=True,null=True)

    user = models.ForeignKey("user.Reader",on_delete = models.SET_NULL,null=True)
