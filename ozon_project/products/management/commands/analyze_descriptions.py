import re
from collections import Counter
from django.core.management.base import BaseCommand
from products.models import Product
import nltk
from stop_words import get_stop_words

# Загружаем данные для NLTK (нужно выполнить один раз)
nltk.download('punkt')
stop_words = get_stop_words('ru')


def get_top_words(descriptions, top_n=10):
    all_words = []
    for desc in descriptions:
        if desc:  # Проверяем, что описание не пустое
            # Убираем знаки препинания
            desc = re.sub(r'[^\w\s]', '', desc)
            desc = desc.lower()
            words = nltk.word_tokenize(desc, language='russian')
            words = [word for word in words if word not in stop_words]
            all_words.extend(words)

    word_counts = Counter(all_words)
    return word_counts.most_common(top_n)


class Command(BaseCommand):
    help = 'Анализирует описания товаров и выводит 10 самых популярных слов'

    def handle(self, *args, **kwargs):
        # Получаем все описания товаров
        descriptions = Product.objects.values_list('description', flat=True)
        # Получаем топ-10 слов
        top_words = get_top_words(descriptions)
        self.stdout.write("Топ-10 самых популярных слов в описаниях товаров:")
        for word, count in top_words:
            self.stdout.write(f"{word}: {count}")