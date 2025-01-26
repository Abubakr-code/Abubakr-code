const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

// Telegram Bot API tokenini kiriting
const telegramToken = '7794517010:AAGwNbceU7vv1oHhYo3HivctxWJtAObMgrg';
// OpenWeatherMap API kalitini kiriting
const weatherApiKey = 'f94cde8c5c55029d2fd2ce50e7e7ffd0';

const bot = new TelegramBot(telegramToken, {polling: true});

const cities = ['Tashkent', 'Samarkand', 'Bukhara', 'Khiva'];

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text.toLowerCase();

    if (text.startsWith('/weather')) {
        const city = text.split(' ')[1];
        if (!city) {
            bot.sendMessage(chatId, 'Iltimos, shahar nomini kiriting. Masalan: /weather Tashkent');
            return;
        }

        try {
            const response = await axios.get(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${weatherApiKey}&units=metric`);
            const weather = response.data;
            const temp = weather.main.temp;
            const description = weather.weather[0].description;
            const humidity = weather.main.humidity;

            let message = `Shahar: ${weather.name}\nHarorat: ${temp} °C\nOb-havo: ${description}\nNamlik: ${humidity}%\n`;

            if (humidity > 80) {
                message += "Havo juda nam. Iltimos, maska taqishni unutmang va o'zingizni ehtiyot qiling!";
            } else if (humidity < 50) {
                message += "Bugun havo ochiq ko'rinadi. Tinchlikda yurishingiz mumkin!";
            }

            bot.sendMessage(chatId, message);
        } catch (error) {
            console.error('Xatolik yuz berdi:', error.message);
            bot.sendMessage(chatId, 'Ob-havo ma\'lumotlarini olishda xatolik yuz berdi. Shahar nomini to\'g\'ri kiriting yoki keyinroq urinib ko\'ring.');
        }
    } else if (text === '/cities') {
        const citiesMessage = `Mavjud shaharlar:\n${cities.join('\n')}`;
        bot.sendMessage(chatId, citiesMessage);
    } else if (text === '/time') {
        const now = new Date();
        const timeMessage = `Hozirgi vaqt: ${now.toLocaleString()}`;
        bot.sendMessage(chatId, timeMessage);
    } else {
        bot.sendMessage(chatId, 'Ob-havo ma\'lumotlarini olish uchun /weather [shahar] buyrug\'ini kiriting.\nMavjud shaharlar ro\'yxatini olish uchun /cities buyrug\'ini kiriting.\nHozirgi vaqtni bilish uchun /time buyrug\'ini kiriting.');
    }
});

console.log('Bot ishga tushirildi');