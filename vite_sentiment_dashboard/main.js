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
let subscription = null
let isConnected = false

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
        
        renderChart(data)
        renderLatestScores(data)
        
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