import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [products, setProducts] = useState([]); // Хранит список товаров
  const [loading, setLoading] = useState(true); // Показывает, грузятся ли данные

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/products/');
        setProducts(response.data); // Сохраняем данные из API
        setLoading(false); // Отключаем загрузку
      } catch (error) {
        console.error('Ошибка при получении данных:', error);
        setLoading(false);
      }
    };
    fetchProducts();
  }, []); // Пустой массив значит, что запрос выполнится один раз при загрузке

  if (loading) {
    return <div>Загрузка...</div>; // Показываем, пока данные грузятся
  }

  return (
    <div>
      <h1>Список товаров</h1>
      <ul>
        {products.map(product => (
          <li key={product.id}>
            <strong>{product.offer_id}</strong> - {product.description}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;