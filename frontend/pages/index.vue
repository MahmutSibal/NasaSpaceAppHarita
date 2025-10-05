<template>
  <div class="page">
    <!-- Left Side: Map Container -->
    <div class="map-container">
      <div id="map" ref="mapEl"></div>
    </div>

    <!-- Right Side: Chat Panel -->
    <div class="chat-panel">
      <!-- Chat Header -->
      <div class="chat-header">
        <div class="header-info">
          <h2 class="panel-title">COSMOSTORM</h2>
          <button class="locate-btn" @click="locateMe" title="Mevcut konumumu bul">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="2"/>
              <circle cx="12" cy="4" r="1"/>
              <circle cx="12" cy="20" r="1"/>
              <circle cx="4" cy="12" r="1"/>
              <circle cx="20" cy="12" r="1"/>
              <circle cx="7" cy="7" r="1"/>
              <circle cx="17" cy="7" r="1"/>
              <circle cx="7" cy="17" r="1"/>
              <circle cx="17" cy="17" r="1"/>
            </svg>
          </button>
          <div class="status-indicator active"></div>
        </div>
        <div class="panel-subtitle">Weather Intelligence</div>
      </div>

      <!-- Chat Messages -->
      <div class="chat-messages" ref="chatMessagesEl">
        <div v-for="message in chatMessages" :key="message.id" class="message" :class="message.type">
          <div class="message-content" v-html="message.text"></div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </div>
      
      <!-- Chat Input -->
      <div class="chat-input">
        <input 
          v-model="chatInput" 
          @keyup.enter="sendMessage"
          :placeholder="chatStep === 'city' ? 'Hangi şehir? (örn: İstanbul, Diyarbakır, Paris)' : `${selectedCity?.name || selectedCity?.city} için ne öğrenmek istiyorsunuz? (örn: bugün hava, haftalık tahmin, yarın yağmur var mı)`"
          :disabled="isSearching"
          class="input-field"
        />
        <button @click="sendMessage" :disabled="isSearching || !chatInput.trim()" class="send-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const mapEl = ref(null)
const chatMessagesEl = ref(null)
let L = null
let map = null

// Chat state
const chatInput = ref('')
const chatMessages = ref([])
const isSearching = ref(false)
let messageIdCounter = 0

// Two-step interaction state
const chatStep = ref('city') // 'city' or 'question'
const selectedCity = ref(null)
const isWaitingForCity = ref(true)

// Current weather panel state
const currentWeather = ref(null)
const updatedAt = ref(0)
const currentCenter = reactive({ lat: 0, lng: 0 })
const units = 'metric' // Always use metric units

// Favorite cities
const favoriteCities = ref([])

function fmt(v, unit = '') {
  if (v === null || v === undefined || Number.isNaN(v)) return '-'
  return `${Number(v).toFixed(1)}${unit}`
}

// Chat message helper
function addMessage(text, type = 'system') {
  const message = {
    id: messageIdCounter++,
    text,
    type,
    time: new Date().toLocaleTimeString()
  }
  chatMessages.value.push(message)
  
  // Auto scroll to bottom
  nextTick(() => {
    if (chatMessagesEl.value) {
      chatMessagesEl.value.scrollTop = chatMessagesEl.value.scrollHeight
    }
  })
}

// Geocoding with Nominatim (OpenStreetMap)
async function searchLocation(query) {
  try {
    // First try: exact search
    let url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=3&addressdetails=1&accept-language=tr,en`
    let response = await fetch(url)
    
    if (!response.ok) throw new Error('Geocoding failed')
    
    let results = await response.json()
    
    // If no results, try with Turkey country constraint
    if (results.length === 0) {
      const queryWithTurkey = `${query}, Turkey`
      url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryWithTurkey)}&limit=3&addressdetails=1&accept-language=tr,en`
      response = await fetch(url)
      
      if (response.ok) {
        results = await response.json()
      }
    }
    
    // If still no results, try common Turkish city name mappings
    if (results.length === 0) {
      const turkishCityMappings = {
        'diyarbakir': 'Diyarbakır',
        'izmir': 'İzmir', 
        'ankara': 'Ankara',
        'istanbul': 'İstanbul',
        'antalya': 'Antalya',
        'bursa': 'Bursa',
        'adana': 'Adana',
        'konya': 'Konya',
        'gaziantep': 'Gaziantep',
        'mersin': 'Mersin'
      }
      
      const lowerQuery = query.toLowerCase()
      const mappedCity = turkishCityMappings[lowerQuery]
      
      if (mappedCity) {
        url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(mappedCity + ', Turkey')}&limit=3&addressdetails=1&accept-language=tr,en`
        response = await fetch(url)
        
        if (response.ok) {
          results = await response.json()
        }
      }
    }
    
    if (results.length === 0) {
      return null
    }
    
    // Prefer cities over other location types
    const cityResult = results.find(r => 
      r.address?.city || r.address?.town || r.address?.municipality || 
      r.type === 'city' || r.type === 'town' || r.type === 'administrative'
    ) || results[0]
    
    return {
      lat: parseFloat(cityResult.lat),
      lng: parseFloat(cityResult.lon),
      name: cityResult.display_name,
      city: cityResult.address?.city || cityResult.address?.town || cityResult.address?.village || cityResult.address?.municipality,
      country: cityResult.address?.country
    }
  } catch (error) {
    console.error('Geocoding error:', error)
    return null
  }
}

// Favorite cities management
function loadFavoriteCities() {
  try {
    const saved = localStorage.getItem('favoriteCities')
    if (saved) {
      favoriteCities.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('Error loading favorite cities:', error)
    favoriteCities.value = []
  }
}

function saveFavoriteCities() {
  try {
    localStorage.setItem('favoriteCities', JSON.stringify(favoriteCities.value))
  } catch (error) {
    console.error('Error saving favorite cities:', error)
  }
}

function addToFavorites(city) {
  if (!favoriteCities.value.find(fav => fav.name === city.name)) {
    favoriteCities.value.push({
      name: city.name,
      lat: city.lat,
      lng: city.lng,
      city: city.city,
      country: city.country
    })
    saveFavoriteCities()
    addMessage(`${city.name} favorilere eklendi!`, 'success')
  } else {
    addMessage(`${city.name} zaten favorilerinizde bulunuyor.`, 'info')
  }
}

function removeFromFavorites(cityName) {
  const index = favoriteCities.value.findIndex(fav => fav.name === cityName)
  if (index !== -1) {
    favoriteCities.value.splice(index, 1)
    saveFavoriteCities()
    addMessage(`${cityName} favorilerden çıkarıldı.`, 'success')
  }
}

function goToFavoriteCity(city) {
  if (map) {
    map.flyTo([city.lat, city.lng], 10)
    fetchCurrentWeather()
    addMessage(`${city.name} konumuna gidildi.`, 'success')
    
    // Auto-get weather for the favorite city
    setTimeout(async () => {
      addMessage('Bu konumun hava durumu getiriliyor...', 'loading')
      const weatherResponse = await getChatWeatherResponse(city.lat, city.lng, "bugün hava durumu nasıl")
      
      if (weatherResponse) {
        addMessage(weatherResponse.response.replace(/\n/g, '<br>'), 'weather')
      }
    }, 1000)
  }
}

// Backend API calls
async function getWeatherFromAPI(lat, lon) {
  try {
    const response = await fetch('http://localhost:8000/weather', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        units: units
      })
    })
    
    if (!response.ok) throw new Error('API request failed')
    
    return await response.json()
  } catch (error) {
    console.error('Backend API error:', error)
    return null
  }
}

async function getChatWeatherResponse(lat, lon, message) {
  try {
    const response = await fetch('http://localhost:8000/chat/weather', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        units: units,
        message: message
      })
    })
    
    if (!response.ok) throw new Error('Chat API request failed')
    
    return await response.json()
  } catch (error) {
    console.error('Chat API error:', error)
    return null
  }
}

async function getWeeklyForecast(lat, lon) {
  try {
    const response = await fetch('http://localhost:8000/forecast/weekly', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        units: units
      })
    })
    
    if (!response.ok) throw new Error('Weekly forecast request failed')
    
    return await response.json()
  } catch (error) {
    console.error('Weekly forecast API error:', error)
    return null
  }
}

async function getTomorrowForecast(lat, lon) {
  try {
    const response = await fetch('http://localhost:8000/forecast/tomorrow', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        units: units
      })
    })
    
    if (!response.ok) throw new Error('Tomorrow forecast request failed')
    
    return await response.json()
  } catch (error) {
    console.error('Tomorrow forecast API error:', error)
    return null
  }
}

// Smart location extraction and command detection
function analyzeMessage(message) {
  const lowerMessage = message.toLowerCase()
  
  // Detect command types
  const isWeeklyForecast = /\b(hafta|week|7\s*g[üu]n|bu\s*hafta|haftal[ıi]k)\b/i.test(lowerMessage)
  const isTomorrowQuery = /\b(yar[ıi]n|tomorrow)\b/i.test(lowerMessage)
  const isHourlyQuery = /\b(saatlik|hourly|saat\s*saat|24\s*saat)\b/i.test(lowerMessage)
  const isTodayQuery = /\b(bug[üu]n|today|şimdi|şu\s*an)\b/i.test(lowerMessage)
  const isThisWeekQuery = /\b(bu\s*hafta|this\s*week)\b/i.test(lowerMessage)
  const isCurrentQuery = /\b(şu\s*an|şimdi|now|current|mevcut)\b/i.test(lowerMessage)
  
  // Favorite city commands
  const isAddFavoriteCommand = /\b(favorilere\s*ekle|add\s*favorite|fav\s*ekle)\b/i.test(lowerMessage)
  const isListFavoritesCommand = /\b(favorilerim|favoriler|favorites|favs|favorite\s*list)\b/i.test(lowerMessage)
  const isRemoveFavoriteCommand = /\b(favorilerden\s*çıkar|remove\s*favorite|fav\s*sil)\b/i.test(lowerMessage)
  
  // Weather keywords - expanded list
  const weatherKeywords = ['hava', 'sıcaklık', 'yağmur', 'kar', 'rüzgar', 'bugün', 'weather', 'derece', 'soğuk', 'sıcak', 'nasıl', 'durum', 'kaç', 'nem', 'basınç', 'uv', 'yağar', 'yağış', 'tahmin']
  const isWeatherQuestion = weatherKeywords.some(keyword => lowerMessage.includes(keyword))
  
  // Enhanced location extraction patterns
  const locationPatterns = [
    // "Diyarbakır'da bu hafta yağmur yağar mı"
    /(\w+(?:\s+\w+)*?)(?:\s*(?:'?da|'?de|'?ta|'?te))?\s+(?:bu\s+hafta|hafta|haftalık|hava|weather|sıcaklık|derece|yağmur|yağar)/i,
    // "Diyarbakır haftalık hava"
    /^(\w+(?:\s+\w+)*?)\s+(?:haftalık|hafta|hava|weather|sıcaklık|derece)/i,
    // "Istanbul'da kaç derece"
    /(\w+(?:\s+\w+)*?)\s*(?:'?da|'?de|'?ta|'?te)\s+(?:hava|kaç|sıcaklık|derece|yağmur|nasıl)/i,
    // "New York'ta hava nasıl"
    /(\w+(?:\s+\w+)*?)\s*(?:'?ta|'?te|'?da|'?de|hava|weather|sıcaklık|derece)/i,
    // "How is weather in Paris"
    /(?:weather\s+in\s+|hava\s+.*?)\s*(\w+(?:\s+\w+)*)/i,
    // Just city name at the beginning
    /^(\w+(?:\s+\w+)*?)\s+(?:hava|weather|sıcaklık|derece|nasıl|hafta|yağmur|yağar)/i
  ]
  
  let extractedLocation = null
  for (const pattern of locationPatterns) {
    const match = lowerMessage.match(pattern)
    if (match && match[1]) {
      let location = match[1].trim()
      // Clean up common Turkish suffixes and common words
      location = location.replace(/'?(ta|te|da|de|nın|nin|nun|nün)$/i, '')
      location = location.replace(/\b(bu|şu|this|that)\s+/i, '')
      
      // Skip if location is too short or contains only common words
      if (location.length > 2 && !['bu', 'şu', 'bu hafta', 'hafta'].includes(location.toLowerCase())) {
        extractedLocation = location
        break
      }
    }
  }
  
  return {
    isWeatherQuestion,
    isWeeklyForecast,
    isTomorrowQuery,
    isHourlyQuery,
    isTodayQuery,
    isThisWeekQuery,
    isCurrentQuery,
    isAddFavoriteCommand,
    isListFavoritesCommand,
    isRemoveFavoriteCommand,
    extractedLocation
  }
}

async function sendMessage() {
  const query = chatInput.value.trim()
  if (!query || isSearching.value) return
  
  // Add user message
  addMessage(query, 'user')
  
  // Clear input
  chatInput.value = ''
  isSearching.value = true
  
  // Handle two-step interaction
  if (chatStep.value === 'city') {
    // Step 1: City selection
    await handleCitySelection(query)
  } else if (chatStep.value === 'question') {
    // Step 2: Weather question
    await handleWeatherQuestion(query)
  }
  
  isSearching.value = false
}

async function handleCitySelection(query) {
  // Handle favorite city commands
  const analysis = analyzeMessage(query)
  
  if (analysis.isListFavoritesCommand) {
    if (favoriteCities.value.length === 0) {
      addMessage('Henüz favori şehriniz bulunmuyor.', 'info')
    } else {
      let favoritesText = 'FAVORI ŞEHIRLER:\n\n'
      favoriteCities.value.forEach((city, index) => {
        favoritesText += `${index + 1}. ${city.city || city.name} (${city.country || 'Ülke bilgisi yok'})\n`
      })
      favoritesText += '\nBir şehir seçmek için numarasını yazın!'
      addMessage(favoritesText.replace(/\n/g, '<br>'), 'info')
    }
    return
  }
  
  // Check if user is selecting a favorite city by number
  const favoriteIndex = parseInt(query) - 1
  if (!isNaN(favoriteIndex) && favoriteIndex >= 0 && favoriteIndex < favoriteCities.value.length) {
    const favoriteCity = favoriteCities.value[favoriteIndex]
    selectedCity.value = favoriteCity
    
    // Move map to selected city
    if (map) {
      map.flyTo([favoriteCity.lat, favoriteCity.lng], 10)
      await fetchCurrentWeather()
    }
    
    addMessage(`${favoriteCity.city || favoriteCity.name} seçildi!`, 'success')
    addMessage('Bu şehir için ne öğrenmek istiyorsunuz?', 'info')
    addMessage('Örnek sorular: "bugün hava nasıl", "haftalık tahmin", "yarın yağmur var mı", "sıcaklık kaç derece"', 'info')
    
    chatStep.value = 'question'
    return
  }
  
  // Check if user is trying to select a favorite city by name
  const favoriteCity = favoriteCities.value.find(fav => 
    fav.city?.toLowerCase().includes(query.toLowerCase()) || 
    fav.name?.toLowerCase().includes(query.toLowerCase())
  )
  
  if (favoriteCity) {
    selectedCity.value = favoriteCity
    
    // Move map to selected city
    if (map) {
      map.flyTo([favoriteCity.lat, favoriteCity.lng], 10)
      await fetchCurrentWeather()
    }
    
    addMessage(`${favoriteCity.city || favoriteCity.name} seçildi!`, 'success')
    addMessage('Bu şehir için ne öğrenmek istiyorsunuz?', 'info')
    addMessage('Örnek sorular: "bugün hava nasıl", "haftalık tahmin", "yarın yağmur var mı", "sıcaklık kaç derece"', 'info')
    
    chatStep.value = 'question'
    return
  }
  
  // Search for new city
  addMessage(`"${query}" şehri aranıyor...`, 'loading')
  
  const location = await searchLocation(query)
  
  if (location) {
    selectedCity.value = location
    
    // Move map to selected city
    if (map) {
      map.flyTo([location.lat, location.lng], 10)
      await fetchCurrentWeather()
    }
    
    addMessage(`${location.city || location.name} şehri bulundu ve seçildi!`, 'success')
    
    // Suggest adding to favorites
    if (!favoriteCities.value.find(fav => fav.name === location.name)) {
      addMessage(`Bu şehri favorilerinize eklemek için "favorilere ekle" yazın.`, 'info')
      window.lastFoundLocation = location
    }
    
    addMessage('Bu şehir için ne öğrenmek istiyorsunuz?', 'info')
    addMessage('Örnek sorular: "bugün hava nasıl", "haftalık tahmin", "yarın yağmur var mı", "sıcaklık kaç derece"', 'info')
    
    chatStep.value = 'question'
  } else {
    addMessage(`"${query}" şehri bulunamadı.`, 'error')
    addMessage('Lütfen farklı bir şehir adı deneyin. Örnek: İstanbul, Diyarbakır, Paris, New York', 'info')
  }
}

async function handleWeatherQuestion(query) {
  if (!selectedCity.value) {
    addMessage('Önce bir şehir seçmelisiniz.', 'error')
    chatStep.value = 'city'
    return
  }
  
  // Handle favorite commands in question step
  const analysis = analyzeMessage(query)
  
  if (analysis.isAddFavoriteCommand) {
    if (window.lastFoundLocation) {
      addToFavorites(window.lastFoundLocation)
      window.lastFoundLocation = null
    } else if (selectedCity.value) {
      addToFavorites(selectedCity.value)
    }
    return
  }
  
  // Handle "new city" or "change city" commands
  if (query.toLowerCase().includes('yeni şehir') || query.toLowerCase().includes('şehir değiştir') || query.toLowerCase().includes('başka şehir')) {
    addMessage('Yeni şehir seçimi için hangi şehri istiyorsunuz?', 'info')
    chatStep.value = 'city'
    selectedCity.value = null
    return
  }
  
  // Analyze weather question
  const city = selectedCity.value
  
  if (analysis.isWeeklyForecast) {
    addMessage(`${city.city || city.name} için 7 günlük tahmin getiriliyor...`, 'loading')
    const weeklyResponse = await getWeeklyForecast(city.lat, city.lng)
    
    if (weeklyResponse) {
      addMessage(weeklyResponse.forecast.replace(/\n/g, '<br>'), 'weather')
    } else {
      addMessage('Haftalık tahmin şu anda alınamıyor.', 'error')
    }
  } else if (analysis.isTomorrowQuery) {
    addMessage(`${city.city || city.name} için yarın hava tahmini getiriliyor...`, 'loading')
    const tomorrowResponse = await getTomorrowForecast(city.lat, city.lng)
    
    if (tomorrowResponse) {
      addMessage(tomorrowResponse.forecast.replace(/\n/g, '<br>'), 'weather')
    } else {
      addMessage('Yarın hava tahmini şu anda alınamıyor.', 'error')
    }
  } else {
    // General weather info
    addMessage(`${city.city || city.name} için hava durumu bilgileri getiriliyor...`, 'loading')
    const weatherResponse = await getChatWeatherResponse(city.lat, city.lng, query)
    
    if (weatherResponse) {
      addMessage(weatherResponse.response.replace(/\n/g, '<br>'), 'weather')
    } else {
      addMessage('Hava durumu verileri şu anda alınamıyor.', 'error')
    }
  }
  
  // Ask if user wants to ask another question
  addMessage('Başka bir soru sormak ister misiniz? Veya "yeni şehir" yazarak farklı bir şehir seçebilirsiniz.', 'info')
}

// ----- Current weather (Open-Meteo) -----
async function fetchCurrentWeather() {
  if (!map) return
  const c = map.getCenter()
  currentCenter.lat = c.lat
  currentCenter.lng = c.lng
  
  const weather = await getWeatherFromAPI(c.lat, c.lng)
  if (weather) {
    currentWeather.value = weather
    updatedAt.value = Date.now()
  }
}

// ----- Map interaction -----
function locateMe() {
  if (!navigator.geolocation) return
  navigator.geolocation.getCurrentPosition(pos => {
    const { latitude, longitude } = pos.coords
    if (map) {
      map.flyTo([latitude, longitude], 8)
      fetchCurrentWeather()
    }
  })
}

let weatherTimer
function startWeatherAutoRefresh() {
  if (weatherTimer) clearInterval(weatherTimer)
  weatherTimer = setInterval(fetchCurrentWeather, 60_000 * 10) // 10 minutes
}

onMounted(async () => {
  // Lazy-load Leaflet on client to avoid SSR issues
  const leaflet = await import('leaflet')
  L = leaflet.default
  if (!mapEl.value) return
  map = L.map(mapEl.value, {
    center: [20, 0],
    zoom: 2,
    worldCopyJump: false, // Dünya tekrarı kapalı
    maxBounds: [[-60, -180], [85, 180]], // Sınırlar: -60° (güney sınırı) / +85° (kuzey sınırı)
    maxBoundsViscosity: 1.0, // Sert sınır - dışarı çıkamaz
    minZoom: 1, // Minimum zoom - çok uzaklaşamaz
    maxZoom: 18 // Maximum zoom
  })

  // Sadece topografik harita
  const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap (CC-BY-SA)',
    noWrap: true // Tekrarlamayı engelle
  })
  
  topoLayer.addTo(map)
  L.control.scale({ metric: true, imperial: true }).addTo(map)

  map.on('moveend zoomend', () => { fetchCurrentWeather() })
  
  // Initial weather fetch
  await fetchCurrentWeather()
  startWeatherAutoRefresh()
  
  // Load favorite cities from localStorage
  loadFavoriteCities()
  
  // Welcome message for two-step system
  addMessage('COSMOSTORM Weather Intelligence System', 'system')
  addMessage('Hangi şehrin hava durumunu öğrenmek istiyorsunuz?', 'info')
  
  if (favoriteCities.value.length > 0) {
    addMessage('Favori şehirlerinizi görmek için "favorilerim" yazın.', 'info')
  }
  
  addMessage('Şehir örnekleri: İstanbul, Diyarbakır, Paris, New York, Tokyo...', 'info')
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
  if (weatherTimer) clearInterval(weatherTimer)
})
</script>

<style scoped>
.page {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

/* Left Side: Map Container */
.map-container {
  flex: 1;
  position: relative;
  height: 100vh;
}

#map {
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* Right Side: Chat Panel */
.chat-panel {
  width: 400px;
  height: 100vh;
  background: linear-gradient(145deg, #1a1f3a 0%, #2d3561 100%);
  border-left: 1px solid rgba(102, 126, 234, 0.2);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.chat-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Chat Header */
.chat-header {
  padding: 25px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.panel-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(45deg, #667eea, #ffd700);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  letter-spacing: 1px;
}

.locate-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 8px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.locate-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
  transform: scale(1.05);
  color: #ffd700;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #51cf66;
  box-shadow: 0 0 15px rgba(81, 207, 102, 0.6);
  animation: pulse 2s infinite;
}

.panel-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* Message Styles */
.message {
  margin: 15px 0;
  padding: 15px 18px;
  border-radius: 20px;
  font-size: 14px;
  line-height: 1.6;
  max-width: 90%;
  word-wrap: break-word;
  position: relative;
  animation: messageSlideIn 0.4s ease-out;
}

.message.user {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 8px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.message.system {
  background: rgba(255, 255, 255, 0.08);
  color: #e3f2fd;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-left: 4px solid #667eea;
  border-bottom-left-radius: 8px;
}

.message.weather {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.15), rgba(3, 169, 244, 0.15));
  color: #e1f5fe;
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-left: 4px solid #2196f3;
  border-bottom-left-radius: 8px;
}

.message.info {
  background: rgba(76, 175, 80, 0.15);
  color: #e8f5e8;
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-left: 4px solid #4caf50;
  border-bottom-left-radius: 8px;
}

.message.success {
  background: rgba(76, 175, 80, 0.2);
  color: #e8f5e8;
  border: 1px solid rgba(76, 175, 80, 0.4);
  border-left: 4px solid #4caf50;
  border-bottom-left-radius: 8px;
}

.message.error {
  background: rgba(244, 67, 54, 0.15);
  color: #ffebee;
  border: 1px solid rgba(244, 67, 54, 0.3);
  border-left: 4px solid #f44336;
  border-bottom-left-radius: 8px;
}

.message.loading {
  background: rgba(255, 193, 7, 0.15);
  color: #fff8e1;
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-left: 4px solid #ffc107;
  border-bottom-left-radius: 8px;
  animation: loadingPulse 1.5s infinite;
}

.message-content {
  margin-bottom: 6px;
  font-weight: 400;
}

.message-time {
  font-size: 11px;
  opacity: 0.6;
  text-align: right;
  font-weight: 300;
}

/* Chat Input */
.chat-input {
  display: flex;
  padding: 20px;
  gap: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  position: relative;
  z-index: 1;
}

.input-field {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-family: inherit;
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-field:focus {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 0 25px rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.1);
}

.send-btn {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Animations */
@keyframes pulse {
  0%, 100% { 
    opacity: 1; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.7; 
    transform: scale(1.1);
  }
}

@keyframes messageSlideIn {
  0% {
    opacity: 0;
    transform: translateY(15px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes loadingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .page {
    flex-direction: column;
  }
  
  .map-container {
    height: 60vh;
  }
  
  .chat-panel {
    width: 100%;
    height: 40vh;
    border-left: none;
    border-top: 1px solid rgba(102, 126, 234, 0.2);
  }
  
  .input-field {
    font-size: 16px; /* Prevent zoom on iOS */
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 20px 15px;
  }
  
  .chat-messages {
    padding: 15px;
  }
  
  .chat-input {
    padding: 15px;
  }
  
  .message {
    padding: 12px 15px;
    font-size: 13px;
  }
}
</style>