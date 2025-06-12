// ===== main.js =====
import { createClient } from '@supabase/supabase-js'
import Plotly from 'plotly.js-dist'

// Access environment variables (available at build time)
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

console.log('Environment check:')
console.log('Supabase URL:', supabaseUrl ? 'Present' : 'Missing')
console.log('Supabase Key:', supabaseKey ? 'Present' : 'Missing')

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase environment variables')
    document.getElementById('latest-content').innerHTML = 
        '<p style="color: #f44336;">Configuration error. Please check environment variables.</p>'
    throw new Error('Missing Supabase configuration')
}

const supabase = createClient(supabaseUrl, supabaseKey)

// Global state
let currentData = null
let smoothedData = null
let subscription = null
let isConnected = false
let currentAlpha = 0.033 // Default alpha for ~1 hour EMA

// Utility functions
function scoreToColor(score) {
    const clampedScore = Math.max(-1, Math.min(1, score))
    const red = Math.floor(255 * (1 - Math.max(clampedScore, 0)))
    const green = Math.floor(255 * (1 + Math.min(clampedScore, 0)))
    return `rgb(${red}, ${green}, 150)`
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'UTC',
        timeZoneName: 'short'
    })
}

function showUpdateIndicator() {
    const indicator = document.getElementById('update-indicator')
    indicator.classList.add('show')
    setTimeout(() => {
        indicator.classList.remove('show')
    }, 2000)
}

function updateConnectionStatus(connected, message = '') {
    const statusElement = document.getElementById('connection-status')
    const statusText = document.getElementById('status-text')
    
    isConnected = connected
    
    if (connected) {
        statusElement.className = 'status connected'
        statusText.textContent = `🟢 Real-time updates active ${message}`
    } else {
        statusElement.className = 'status disconnected'
        statusText.textContent = `🔴 Real-time updates disconnected ${message}`
    }
}

// Data fetching
async function fetchSentimentData(days = 7) {
    const beginDate = new Date()
    beginDate.setDate(beginDate.getDate() - days)
    
    try {
        console.log('Fetching sentiment data...')
        const { data, error } = await supabase
            .from('sentiment_scores')
            .select('*')
            .gte('timestamp', beginDate.toISOString())
            .order('timestamp', { ascending: true })
        
        if (error) {
            console.error('Supabase error:', error)
            throw error
        }
        
        console.log('Fetched data:', data?.length, 'rows')
        
        // Flatten the scores data
        const flattenedData = data.map(row => ({
            timestamp: new Date(row.timestamp),
            ...row.scores
        }))
        
        return flattenedData
    } catch (error) {
        console.error('Error fetching data:', error)
        return []
    }
}

// Chart rendering
function renderChart(data) {
    if (!data || data.length === 0) {
        console.log('No data to render chart')
        return
    }
    
    console.log('Rendering chart with', data.length, 'data points')
    
    // Get all unique tickers
    const tickers = new Set()
    data.forEach(row => {
        Object.keys(row).forEach(key => {
            if (key !== 'timestamp') {
                tickers.add(key)
            }
        })
    })
    
    const tickerArray = Array.from(tickers)
    const traces = []
    
    // Create a trace for each ticker with separate subplot
    tickerArray.forEach((ticker, index) => {
        const x = []
        const y = []
        
        data.forEach(row => {
            if (row[ticker] !== undefined && row[ticker] !== null) {
                x.push(row.timestamp)
                y.push(row[ticker])
            }
        })
        
        if (x.length > 0) {
            traces.push({
                x: x,
                y: y,
                type: 'scatter',
                mode: 'lines+markers',
                name: ticker,
                line: { width: 2 },
                marker: { size: 4 },
                xaxis: `x${index + 1}`,
                yaxis: `y${index + 1}`
            })
        }
    })
    
    // Create subplot layout
    const numTickers = tickerArray.length
    const isMobile = window.innerWidth <= 768
    const cols = Math.min(isMobile ? 1 : 3, numTickers)
    const rows = Math.ceil(numTickers / cols)
    
    const layout = {
        paper_bgcolor: '#1e1e2f',
        plot_bgcolor: '#2a2a3e',
        font: { color: 'white' },
        grid: {
            rows: rows,
            columns: cols,
            pattern: 'independent',
            roworder: 'top to bottom'
        },
        margin: { t: 80, r: 50, b: 100, l: 50 },
        showlegend: false,
        height: 220 * rows
    }
    
    // Configure axes for each subplot
    tickerArray.forEach((ticker, index) => {
        const axisNum = index + 1
        layout[`xaxis${axisNum}`] = {
            title: 'Time',
            gridcolor: '#444',
            color: 'white',
            anchor: `y${axisNum}`
        }
        layout[`yaxis${axisNum}`] = {
            title: `${ticker} Sentiment`,
            gridcolor: '#444',
            color: 'white',
            anchor: `x${axisNum}`
        }
    })
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    }
    
    Plotly.newPlot('chart', traces, layout, config)
}

// Table rendering
function renderLatestScores(data) {
    const latestContent = document.getElementById('latest-content')
    const latestTitle = document.getElementById('latest-title')
    
    if (!data || data.length === 0) {
        latestContent.innerHTML = '<p>No data available</p>'
        return
    }
    
    const latestRow = data[data.length - 1]
    const latestTime = formatTimestamp(latestRow.timestamp)
    
    // Get scores (exclude timestamp)
    const scores = { ...latestRow }
    delete scores.timestamp
    
    // Sort scores by value (descending)
    const sortedScores = Object.entries(scores)
        .filter(([_, value]) => value !== null && value !== undefined)
        .sort(([, a], [, b]) => b - a)
    
    latestTitle.textContent = `Latest Scores (as of ${latestTime})`
    
    let tableHTML = `
        <table class="scores-table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th style="text-align: right;">Score</th>
                </tr>
            </thead>
            <tbody>
    `
    
    sortedScores.forEach(([ticker, score]) => {
        const backgroundColor = scoreToColor(score)
        tableHTML += `
            <tr>
                <td>${ticker}</td>
                <td class="score-cell" style="background-color: ${backgroundColor}; color: black;">
                    ${score.toFixed(3)}
                </td>
            </tr>
        `
    })
    
    tableHTML += '</tbody></table>'
    latestContent.innerHTML = tableHTML
}

// Real-time subscription setup
function setupRealtimeSubscription() {
    console.log('Setting up real-time subscription...')
    
    subscription = supabase
        .channel('sentiment-changes')
        .on('postgres_changes', 
            { 
                event: '*', 
                schema: 'public', 
                table: 'sentiment_scores' 
            }, 
            async (payload) => {
                console.log('Real-time update received:', payload)
                showUpdateIndicator()
                
                // Refresh data after any change
                await loadAndRenderData()
                
                // Log the update
                await logVisit('realtime_update')
            }
        )
        .subscribe((status) => {
            console.log('Subscription status:', status)
            
            if (status === 'SUBSCRIBED') {
                updateConnectionStatus(true, '- Live data streaming')
            } else if (status === 'CHANNEL_ERROR') {
                updateConnectionStatus(false, '- Connection error')
            } else if (status === 'TIMED_OUT') {
                updateConnectionStatus(false, '- Connection timed out')
            } else if (status === 'CLOSED') {
                updateConnectionStatus(false, '- Connection closed')
            }
        })
}

// Data loading and rendering
async function loadAndRenderData() {
    try {
        const data = await fetchSentimentData()
        currentData = data
        
        // Apply smoothing and render
        applyAndRenderSmoothing()
        
        if (!isConnected) {
            updateConnectionStatus(false, '- Data loaded, trying to reconnect...')
        }
    } catch (error) {
        console.error('Error loading data:', error)
        document.getElementById('latest-content').innerHTML = 
            '<p style="color: #f44336;">Error loading data. Please refresh the page.</p>'
    }
}

// Logging function
async function logVisit(event) {
    try {
        await supabase
            .from('visit_logs')
            .insert({
                timestamp: new Date().toISOString(),
                event: event
            })
    } catch (error) {
        console.error('Logging failed:', error)
    }
}

// Cleanup function
function cleanup() {
    if (subscription) {
        subscription.unsubscribe()
    }
}

// Initialize the application
async function init() {
    console.log('Initializing sentiment dashboard...')
    
    // Setup UI controls
    setupSmoothingControls()
    
    // Load initial data
    await loadAndRenderData()
    
    // Set up real-time subscription
    setupRealtimeSubscription()
    
    // Log initial visit
    await logVisit('dashboard_load')
    
    // Fallback polling every 5 minutes in case real-time fails
    setInterval(async () => {
        if (!isConnected) {
            console.log('Fallback: Polling for updates...')
            await loadAndRenderData()
        }
    }, 5 * 60 * 1000)
}

// EMA smoothing functions
function applyEMASmoothing(data, alpha) {
    if (!data || data.length === 0 || alpha === 0) {
        return data
    }
    
    // Group data by ticker for independent EMA calculation
    const tickerData = {}
    const timestamps = []
    
    // Collect all unique timestamps and tickers
    data.forEach(row => {
        timestamps.push(row.timestamp)
        Object.keys(row).forEach(key => {
            if (key !== 'timestamp') {
                if (!tickerData[key]) {
                    tickerData[key] = []
                }
                tickerData[key].push({
                    timestamp: row.timestamp,
                    value: row[key]
                })
            }
        })
    })
    
    // Apply EMA to each ticker independently
    const smoothedTickerData = {}
    Object.keys(tickerData).forEach(ticker => {
        const values = tickerData[ticker]
        const smoothed = []
        
        if (values.length > 0) {
            // First value stays the same
            smoothed.push({
                timestamp: values[0].timestamp,
                value: values[0].value
            })
            
            // Apply EMA formula: EMA_t = α * Value_t + (1-α) * EMA_(t-1)
            for (let i = 1; i < values.length; i++) {
                const currentValue = values[i].value
                const previousEMA = smoothed[i-1].value
                const newEMA = alpha * currentValue + (1 - alpha) * previousEMA
                
                smoothed.push({
                    timestamp: values[i].timestamp,
                    value: newEMA
                })
            }
        }
        
        smoothedTickerData[ticker] = smoothed
    })
    
    // Reconstruct the data structure
    const result = []
    timestamps.forEach(timestamp => {
        const row = { timestamp }
        Object.keys(smoothedTickerData).forEach(ticker => {
            const tickerPoint = smoothedTickerData[ticker].find(
                point => point.timestamp.getTime() === timestamp.getTime()
            )
            if (tickerPoint) {
                row[ticker] = tickerPoint.value
            }
        })
        result.push(row)
    })
    
    return result
}

// UI event handlers for smoothing controls
function setupSmoothingControls() {
    const smoothingSelect = document.getElementById('smoothing-select')
    const customContainer = document.getElementById('custom-alpha-container')
    const alphaSlider = document.getElementById('alpha-slider')
    const alphaValue = document.getElementById('alpha-value')
    
    // Handle dropdown change
    smoothingSelect.addEventListener('change', (e) => {
        const value = e.target.value
        
        if (value === 'custom') {
            customContainer.style.display = 'flex'
            currentAlpha = parseFloat(alphaSlider.value)
        } else {
            customContainer.style.display = 'none'
            currentAlpha = parseFloat(value)
        }
        
        // Re-render with new smoothing
        applyAndRenderSmoothing()
    })
    
    // Handle slider change
    alphaSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value)
        alphaValue.textContent = value.toFixed(3)
        currentAlpha = value
        
        // Re-render with new smoothing (debounced)
        clearTimeout(alphaSlider.debounceTimer)
        alphaSlider.debounceTimer = setTimeout(() => {
            applyAndRenderSmoothing()
        }, 200)
    })
}

function applyAndRenderSmoothing() {
    if (!currentData) return
    
    console.log('Applying smoothing with alpha:', currentAlpha)
    smoothedData = applyEMASmoothing(currentData, currentAlpha)
    
    renderChart(smoothedData)
    renderLatestScores(smoothedData)
}

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        cleanup()
    } else {
        setupRealtimeSubscription()
        loadAndRenderData()
    }
})

// Handle page unload
window.addEventListener('beforeunload', cleanup)

// Start the application
init()