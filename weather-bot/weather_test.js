const axios = require('axios');

// API kalitini kiriting
const weatherApiKey = 'f94cde8c5c55029d2fd2ce50e7e7ffd0';
// Shahar nomini kiriting
const city = 'Tashkent';


axios.get(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${weatherApiKey}&units=metric`)
    .then(response => {
        const weather = response.data;
        console.log(`Shahar: ${weather.name}`);
        console.log(`Harorat: ${weather.main.temp} °C`);
        console.log(`Ob-havo: ${weather.weather[0].description}`);
    })
    .catch(error => {
        console.log('Xatolik yuz berdi:', error);
    });