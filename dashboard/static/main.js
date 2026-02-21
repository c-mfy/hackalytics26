/* 
    fetches JSON from /results endpoint 
    generates bar charts/other charts
    logic for graph/globe generation display
**/

/* ─── DATA ─────────────────────────────────────────────────────────────────── */
/** replace with real stuff later */
const MODELS = {
    whisper: {
      label: 'Whisper (OpenAI)',
      accents: [
        { accent: 'American',    flag: '🇺🇸', country: 'US',  wer: 8.1,  coords: [-98,  38] },
        { accent: 'British',     flag: '🇬🇧', country: 'UK',  wer: 12.3, coords: [-2,   54] },
        { accent: 'Australian',  flag: '🇦🇺', country: 'AU',  wer: 14.7, coords: [134, -26] },
        { accent: 'Canadian',    flag: '🇨🇦', country: 'CA',  wer: 10.2, coords: [-96,  56] },
        { accent: 'Indian',      flag: '🇮🇳', country: 'IN',  wer: 22.5, coords: [79,   22] },
        { accent: 'Nigerian',    flag: '🇳🇬', country: 'NG',  wer: 41.7, coords: [8,    10] },
        { accent: 'Scottish',    flag: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', country: 'GB', wer: 19.8, coords: [-4,   57] },
        { accent: 'Irish',       flag: '🇮🇪', country: 'IE',  wer: 16.4, coords: [-8,   53] },
        { accent: 'South African',flag: '🇿🇦', country: 'ZA', wer: 28.9, coords: [25,  -30] },
        { accent: 'Singaporean', flag: '🇸🇬', country: 'SG',  wer: 31.2, coords: [103,   1] },
        { accent: 'Brazilian',   flag: '🇧🇷', country: 'BR',  wer: 36.4, coords: [-51, -14] },
        { accent: 'French',      flag: '🇫🇷', country: 'FR',  wer: 33.1, coords: [2,    47] },
      ]
    },
    google: {
      label: 'Google Speech-to-Text',
      accents: [
        { accent: 'American',    flag: '🇺🇸', country: 'US',  wer: 9.2,  coords: [-98,  38] },
        { accent: 'British',     flag: '🇬🇧', country: 'UK',  wer: 13.5, coords: [-2,   54] },
        { accent: 'Australian',  flag: '🇦🇺', country: 'AU',  wer: 16.2, coords: [134, -26] },
        { accent: 'Canadian',    flag: '🇨🇦', country: 'CA',  wer: 11.4, coords: [-96,  56] },
        { accent: 'Indian',      flag: '🇮🇳', country: 'IN',  wer: 27.8, coords: [79,   22] },
        { accent: 'Nigerian',    flag: '🇳🇬', country: 'NG',  wer: 48.3, coords: [8,    10] },
        { accent: 'Scottish',    flag: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', country: 'GB', wer: 22.1, coords: [-4,   57] },
        { accent: 'Irish',       flag: '🇮🇪', country: 'IE',  wer: 18.9, coords: [-8,   53] },
        { accent: 'South African',flag: '🇿🇦', country: 'ZA', wer: 33.4, coords: [25,  -30] },
        { accent: 'Singaporean', flag: '🇸🇬', country: 'SG',  wer: 37.5, coords: [103,   1] },
        { accent: 'Brazilian',   flag: '🇧🇷', country: 'BR',  wer: 42.1, coords: [-51, -14] },
        { accent: 'French',      flag: '🇫🇷', country: 'FR',  wer: 39.6, coords: [2,    47] },
      ]
    },
    azure: {
      label: 'Azure Speech',
      accents: [
        { accent: 'American',    flag: '🇺🇸', country: 'US',  wer: 11.0, coords: [-98,  38] },
        { accent: 'British',     flag: '🇬🇧', country: 'UK',  wer: 14.8, coords: [-2,   54] },
        { accent: 'Australian',  flag: '🇦🇺', country: 'AU',  wer: 17.9, coords: [134, -26] },
        { accent: 'Canadian',    flag: '🇨🇦', country: 'CA',  wer: 13.1, coords: [-96,  56] },
        { accent: 'Indian',      flag: '🇮🇳', country: 'IN',  wer: 31.2, coords: [79,   22] },
        { accent: 'Nigerian',    flag: '🇳🇬', country: 'NG',  wer: 52.6, coords: [8,    10] },
        { accent: 'Scottish',    flag: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', country: 'GB', wer: 26.7, coords: [-4,   57] },
        { accent: 'Irish',       flag: '🇮🇪', country: 'IE',  wer: 21.5, coords: [-8,   53] },
        { accent: 'South African',flag: '🇿🇦', country: 'ZA', wer: 37.2, coords: [25,  -30] },
        { accent: 'Singaporean', flag: '🇸🇬', country: 'SG',  wer: 41.8, coords: [103,   1] },
        { accent: 'Brazilian',   flag: '🇧🇷', country: 'BR',  wer: 45.3, coords: [-51, -14] },
        { accent: 'French',      flag: '🇫🇷', country: 'FR',  wer: 43.1, coords: [2,    47] },
      ]
    }
  };
  
  const ERROR_EXAMPLES = [
    {
      accent: 'Indian 🇮🇳',
      wer: 22.5,
      reference: 'Please schedule a meeting for Thursday afternoon.',
      hypothesis: 'Please shegule a meating for Tursday afternoon.',
      errors: [
        { type: 'sub', word: 'shegule', correct: 'schedule' },
        { type: 'sub', word: 'meating', correct: 'meeting' },
        { type: 'sub', word: 'Tursday', correct: 'Thursday' },
      ]
    },
    {
      accent: 'Nigerian 🇳🇬',
      wer: 41.7,
      reference: 'The water bottle is on the kitchen counter near the window.',
      hypothesis: 'De water boddle is on de kitchen kounter near de window.',
      errors: [
        { type: 'sub', word: 'De', correct: 'The' },
        { type: 'sub', word: 'boddle', correct: 'bottle' },
        { type: 'sub', word: 'de', correct: 'the' },
        { type: 'sub', word: 'kounter', correct: 'counter' },
      ]
    },
    {
      accent: 'Scottish 🏴󠁧󠁢󠁳󠁣󠁴󠁿',
      wer: 19.8,
      reference: 'I cannot believe how cold it is outside today.',
      hypothesis: 'I cannae believe how cauld it is ootside today.',
      errors: [
        { type: 'sub', word: 'cannae', correct: 'cannot' },
        { type: 'sub', word: 'cauld', correct: 'cold' },
        { type: 'sub', word: 'ootside', correct: 'outside' },
      ]
    },
    {
      accent: 'Singaporean 🇸🇬',
      wer: 31.2,
      reference: 'Can you help me find the nearest subway station?',
      hypothesis: 'Can you help me find nearest MRT station lah?',
      errors: [
        { type: 'del', word: 'the' },
        { type: 'sub', word: 'MRT', correct: 'subway' },
        { type: 'ins', word: 'lah' },
      ]
    },
    {
      accent: 'Brazilian 🇧🇷',
      wer: 36.4,
      reference: 'This presentation needs to be finished before the deadline.',
      hypothesis: 'Dis preezentation needs to be feenished before de deadline.',
      errors: [
        { type: 'sub', word: 'Dis', correct: 'This' },
        { type: 'sub', word: 'preezentation', correct: 'presentation' },
        { type: 'sub', word: 'feenished', correct: 'finished' },
        { type: 'sub', word: 'de', correct: 'the' },
      ]
    }
  ];
  
  /* ─── STATE ──────────────────────────────────────────────────────────────────*/
  
  let activeModel = 'whisper';
  let werBarChart, errorTypeChart, systemRadarChart;
  let isRecording = false;
  let recognition = null;
  let exampleOffset = 0;
  
  /* ─── FETCH / INIT ───────────────────────────────────────────────────────────*/
  
  async function fetchResults(model) {
    try {
      const res = await fetch(`/results?model=${model}`);
      if (!res.ok) throw new Error('Not OK');
      return await res.json();
    } catch {
      // Fallback to mock data for development / demo
      return MODELS[model];
    }
  }
  
  async function init() {
    const data = await fetchResults(activeModel);
    renderAll(data);
  }
  
  /* ─── SWITCH MODEL ───────────────────────────────────────────────────────────*/
  
  async function switchModel(model) {
    activeModel = model;
    document.querySelectorAll('.model-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
  
    const data = await fetchResults(model);
    renderAll(data);
  }
  
  function renderAll(data) {
    const sorted = [...data.accents].sort((a, b) => b.wer - a.wer);
    updateStatCards(data.accents);
    renderWerBarChart(sorted);
    renderWerTable(sorted);
    renderGlobe(data.accents);
    renderErrorExamples();
  }
  
  /* ─── STAT CARDS ─────────────────────────────────────────────────────────────*/
  
  function updateStatCards(accents) {
    const avg = (accents.reduce((s, a) => s + a.wer, 0) / accents.length).toFixed(1);
    document.getElementById('avg-wer').innerHTML =
      `${avg}<span style="font-size:20px;color:var(--text-dim)">%</span>`;
  }
  
  /* ─── WER BAR CHART ──────────────────────────────────────────────────────────*/
  
  function werColor(wer) {
    if (wer < 15) return 'rgba(184,255,87,0.85)';
    if (wer < 25) return 'rgba(255,149,0,0.85)';
    return 'rgba(255,79,123,0.85)';
  }
  
  function renderWerBarChart(sorted) {
    const ctx = document.getElementById('werBarChart').getContext('2d');
  
    const labels = sorted.map(d => `${d.flag} ${d.accent}`);
    const values = sorted.map(d => d.wer);
    const colors = values.map(werColor);
  
    if (werBarChart) werBarChart.destroy();
  
    werBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderRadius: 5,
          borderSkipped: false,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 700, easing: 'easeOutQuart' },
        plugins: {
          legend: { display: false },
          datalabels: {
            color: '#e6edf3',
            anchor: 'end',
            align: 'end',
            formatter: v => v.toFixed(1) + '%',
            font: { family: "'Space Mono', monospace", size: 10 }
          },
          tooltip: {
            backgroundColor: '#141b24',
            borderColor: '#1e2d3d',
            borderWidth: 1,
            titleColor: '#e6edf3',
            bodyColor: '#8b949e',
            callbacks: {
              label: ctx => ` WER: ${ctx.raw.toFixed(1)}%`
            }
          }
        },
        scales: {
          x: {
            max: 60,
            grid: { color: 'rgba(30,45,61,0.5)' },
            ticks: {
              color: '#4a5568',
              font: { family: "'Space Mono', monospace", size: 10 },
              callback: v => v + '%'
            }
          },
          y: {
            grid: { display: false },
            ticks: {
              color: '#8b949e',
              font: { family: "'Space Mono', monospace", size: 11 }
            }
          }
        }
      },
      plugins: [ChartDataLabels]
    });
  }
  
  /* ─── ERROR TYPE DONUT ───────────────────────────────────────────────────────*/
  
  function renderErrorTypeChart() {
    const ctx = document.getElementById('errorTypeChart').getContext('2d');
  
    if (errorTypeChart) errorTypeChart.destroy();
  
    errorTypeChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Substitutions', 'Deletions', 'Insertions'],
        datasets: [{
          data: [62, 25, 13],
          backgroundColor: ['rgba(255,79,123,0.8)', 'rgba(255,149,0,0.8)', 'rgba(0,229,255,0.7)'],
          borderColor: '#0d1117',
          borderWidth: 3,
          hoverOffset: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        animation: { duration: 800 },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#8b949e',
              font: { family: "'Space Mono', monospace", size: 10 },
              padding: 12,
              boxWidth: 12,
            }
          },
          tooltip: {
            backgroundColor: '#141b24',
            borderColor: '#1e2d3d',
            borderWidth: 1,
            callbacks: { label: c => ` ${c.label}: ${c.raw}%` }
          }
        }
      }
    });
  }
  
  /* ─── SYSTEM RADAR ───────────────────────────────────────────────────────────*/
  
  function renderSystemRadar() {
    const ctx = document.getElementById('systemRadarChart').getContext('2d');
  
    if (systemRadarChart) systemRadarChart.destroy();
  
    systemRadarChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['American', 'British', 'Indian', 'African', 'Asian', 'European'],
        datasets: [
          {
            label: 'Whisper',
            data: [92, 88, 77, 58, 69, 67],
            borderColor: 'rgba(0,229,255,0.8)',
            backgroundColor: 'rgba(0,229,255,0.08)',
            pointBackgroundColor: 'rgba(0,229,255,1)',
            borderWidth: 2,
          },
          {
            label: 'Google',
            data: [91, 87, 72, 52, 62, 60],
            borderColor: 'rgba(255,149,0,0.7)',
            backgroundColor: 'rgba(255,149,0,0.06)',
            pointBackgroundColor: 'rgba(255,149,0,1)',
            borderWidth: 2,
          },
          {
            label: 'Azure',
            data: [89, 85, 69, 47, 58, 57],
            borderColor: 'rgba(255,79,123,0.7)',
            backgroundColor: 'rgba(255,79,123,0.06)',
            pointBackgroundColor: 'rgba(255,79,123,1)',
            borderWidth: 2,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 700 },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#8b949e',
              font: { family: "'Space Mono', monospace", size: 9 },
              boxWidth: 8,
              padding: 8,
            }
          }
        },
        scales: {
          r: {
            min: 40,
            max: 100,
            ticks: { display: false },
            grid: { color: 'rgba(30,45,61,0.6)' },
            pointLabels: {
              color: '#8b949e',
              font: { family: "'Space Mono', monospace", size: 9 }
            },
            angleLines: { color: 'rgba(30,45,61,0.6)' }
          }
        }
      }
    });
  }
  
  /* ─── WER TABLE ──────────────────────────────────────────────────────────────*/
  
  function renderWerTable(sorted) {
    const tbody = document.getElementById('wer-table-body');
    tbody.innerHTML = '';
  
    sorted.forEach((d, i) => {
      const color = werColor(d.wer);
      const bias = d.wer < 15 ? 'Low' : d.wer < 25 ? 'Med' : 'High';
      const biasColor = d.wer < 15 ? 'var(--good)' : d.wer < 25 ? 'var(--warn)' : 'var(--bad)';
  
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="color:var(--text-dim);width:28px">${i + 1}</td>
        <td>
          <div class="accent-flag">
            <span class="flag">${d.flag}</span>
            <span style="color:var(--text-bright)">${d.accent}</span>
          </div>
        </td>
        <td>
          <div class="wer-bar-wrap">
            <div class="wer-bar-bg">
              <div class="wer-bar-fill" style="width:${(d.wer / 60) * 100}%;background:${color}"></div>
            </div>
            <span class="wer-pct" style="color:${color}">${d.wer}%</span>
          </div>
        </td>
        <td><span style="color:${biasColor};font-size:10px;font-weight:700">${bias}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }
  
  /* ─── GLOBE / D3 ─────────────────────────────────────────────────────────────*/
  
  let globeProjection, globePath, isDragging = false;
  let dragStart = null, rotateStart = [0, 0];
  
  function renderGlobe(accents) {
    const container = document.getElementById('globe-svg');
    const W = 380, H = 320;
    const svg = d3.select('#globe-svg').attr('width', W).attr('height', H);
    svg.selectAll('*').remove();
  
    globeProjection = d3.geoOrthographic()
      .scale(130)
      .translate([W / 2, H / 2])
      .clipAngle(90)
      .rotate([20, -20]);
  
    globePath = d3.geoPath().projection(globeProjection);
  
    const sphere = { type: 'Sphere' };
  
    // Ocean background
    svg.append('circle')
      .attr('cx', W / 2).attr('cy', H / 2).attr('r', 130)
      .attr('fill', '#0a1520');
  
    const graticule = d3.geoGraticule()();
  
    // Load world topojson
    d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json').then(world => {
      const land = topojson.feature(world, world.objects.land);
      const countries = topojson.feature(world, world.objects.countries);
  
      // Graticule
      svg.append('path')
        .datum(graticule)
        .attr('d', globePath)
        .attr('fill', 'none')
        .attr('stroke', 'rgba(0,229,255,0.08)')
        .attr('stroke-width', 0.5);
  
      // Land
      svg.append('path')
        .datum(land)
        .attr('d', globePath)
        .attr('fill', '#141b24')
        .attr('stroke', '#1e2d3d')
        .attr('stroke-width', 0.5);
  
      // Glow outline
      svg.append('circle')
        .attr('cx', W / 2).attr('cy', H / 2).attr('r', 130)
        .attr('fill', 'none')
        .attr('stroke', 'rgba(0,229,255,0.15)')
        .attr('stroke-width', 1.5);
  
      // Accent dots
      const colorScale = d3.scaleSequential()
        .domain([0, 55])
        .interpolator(d3.interpolate('#b8ff57', '#ff4f7b'));
  
      const dotsGroup = svg.append('g').attr('class', 'dots');
      const tooltip = document.getElementById('globe-tooltip');
  
      function drawDots() {
        dotsGroup.selectAll('.accent-dot').remove();
  
        accents.forEach(a => {
          const [lon, lat] = a.coords;
          const projected = globeProjection([lon, lat]);
          if (!projected) return;
  
          // Check if behind globe
          const angle = d3.geoDistance({ type: 'Point', coordinates: [lon, lat] }, {
            type: 'Point',
            coordinates: globeProjection.invert([W / 2, H / 2])
          });
          if (angle > Math.PI / 2) return;
  
          const r = 4 + (a.wer / 55) * 10;
  
          dotsGroup.append('circle')
            .attr('class', 'accent-dot')
            .attr('cx', projected[0])
            .attr('cy', projected[1])
            .attr('r', r)
            .attr('fill', colorScale(a.wer))
            .attr('opacity', 0.85)
            .attr('stroke', 'rgba(0,0,0,0.4)')
            .attr('stroke-width', 1)
            .style('cursor', 'pointer')
            .on('mouseover', function (event) {
              tooltip.style.display = 'block';
              tooltip.innerHTML = `<strong>${a.flag} ${a.accent}</strong><br>WER: <span style="color:${colorScale(a.wer)}">${a.wer}%</span>`;
            })
            .on('mousemove', function (event) {
              const rect = container.getBoundingClientRect();
              tooltip.style.left = (event.clientX - rect.left + 12) + 'px';
              tooltip.style.top = (event.clientY - rect.top - 10) + 'px';
            })
            .on('mouseout', function () {
              tooltip.style.display = 'none';
            });
        });
      }
  
      drawDots();
  
      // Drag to rotate
      svg.call(d3.drag()
        .on('start', e => {
          isDragging = true;
          dragStart = [e.x, e.y];
          rotateStart = globeProjection.rotate();
        })
        .on('drag', e => {
          if (!dragStart) return;
          const dx = e.x - dragStart[0];
          const dy = e.y - dragStart[1];
          globeProjection.rotate([
            rotateStart[0] + dx * 0.4,
            rotateStart[1] - dy * 0.4
          ]);
          svg.select('path[datum="graticule"]')?.attr('d', globePath);
          svg.selectAll('path').attr('d', globePath);
          drawDots();
        })
        .on('end', () => { isDragging = false; })
      );
  
      // Auto-rotate
      let t = 0;
      function autoRotate() {
        if (!isDragging) {
          t += 0.15;
          globeProjection.rotate([20 + t, -20]);
          svg.selectAll('path').attr('d', globePath);
          drawDots();
        }
        requestAnimationFrame(autoRotate);
      }
      autoRotate();
    });
  }
  
  /* ─── ERROR EXAMPLES ─────────────────────────────────────────────────────────*/
  
  function renderErrorExamples() {
    const panel = document.getElementById('error-examples-panel');
    const examples = [
      ERROR_EXAMPLES[exampleOffset % ERROR_EXAMPLES.length],
      ERROR_EXAMPLES[(exampleOffset + 1) % ERROR_EXAMPLES.length],
    ];
  
    panel.innerHTML = examples.map(ex => {
      // Build highlighted hypothesis
      const parts = ex.hypothesis.split(' ');
      const highlighted = parts.map(word => {
        const cleanWord = word.replace(/[.,?!]/g, '');
        const err = ex.errors.find(e => e.word === cleanWord || e.word === word);
        if (!err) return word;
        if (err.type === 'sub') return `<span class="err-sub" title="→ ${err.correct}">${word}</span>`;
        if (err.type === 'ins') return `<span class="err-ins">${word} [INS]</span>`;
        if (err.type === 'del') return `<span class="err-del">${word}</span>`;
        return word;
      }).join(' ');
  
      const wc = ex.wer < 20 ? '#b8ff57' : ex.wer < 35 ? '#ff9500' : '#ff4f7b';
  
      return `
        <div class="error-example">
          <div class="error-meta">
            <span class="accent-tag">${ex.accent}</span>
            <span class="wer-tag" style="color:${wc}">${ex.wer}% WER</span>
          </div>
          <div class="transcript-line"><span class="label">REF:</span>${ex.reference}</div>
          <div class="transcript-line"><span class="label">STT:</span>${highlighted}</div>
        </div>
      `;
    }).join('');
  }
  
  function shuffleExamples() {
    exampleOffset = (exampleOffset + 2) % ERROR_EXAMPLES.length;
    renderErrorExamples();
  }
  
  /* ─── WER COMPUTATION (Levenshtein) ──────────────────────────────────────────*/
  
  function computeWER(reference, hypothesis) {
    const ref = reference.toLowerCase().replace(/[^a-z\s]/g, '').split(/\s+/);
    const hyp = hypothesis.toLowerCase().replace(/[^a-z\s]/g, '').split(/\s+/);
  
    const N = ref.length, M = hyp.length;
    const dp = Array.from({ length: N + 1 }, (_, i) =>
      Array.from({ length: M + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
    );
    const ops = Array.from({ length: N + 1 }, () => Array(M + 1).fill(''));
  
    for (let i = 1; i <= N; i++) {
      for (let j = 1; j <= M; j++) {
        if (ref[i - 1] === hyp[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1];
          ops[i][j] = 'M';
        } else {
          const sub = dp[i - 1][j - 1] + 1;
          const del = dp[i - 1][j] + 1;
          const ins = dp[i][j - 1] + 1;
          dp[i][j] = Math.min(sub, del, ins);
          if (dp[i][j] === sub) ops[i][j] = 'S';
          else if (dp[i][j] === del) ops[i][j] = 'D';
          else ops[i][j] = 'I';
        }
      }
    }
  
    // Backtrace counts
    let subs = 0, dels = 0, ins = 0;
    let i = N, j = M;
    while (i > 0 || j > 0) {
      const op = ops[i][j];
      if (i > 0 && j > 0 && op === 'S') { subs++; i--; j--; }
      else if (i > 0 && j > 0 && op === 'M') { i--; j--; }
      else if (i > 0 && op === 'D') { dels++; i--; }
      else { ins++; j--; }
    }
  
    const wer = N > 0 ? ((subs + dels + ins) / N * 100).toFixed(1) : 0;
    return { wer, subs, dels, ins, refLen: N };
  }
  
  /* ─── LIVE RECORDING ─────────────────────────────────────────────────────────*/
  
  function toggleRecording() {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  }
  
  function startRecording() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      simulateLiveDemo(); // Fallback for browsers without Web Speech API
      return;
    }
  
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
  
    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      updateLiveOutput(transcript.trim());
    };
  
    recognition.onerror = () => stopRecording();
    recognition.onend = () => { if (isRecording) recognition.start(); };
  
    recognition.start();
    isRecording = true;
    document.getElementById('mic-btn').classList.add('recording');
    document.getElementById('live-output').textContent = 'Listening...';
  }
  
  function stopRecording() {
    if (recognition) recognition.stop();
    isRecording = false;
    document.getElementById('mic-btn').classList.remove('recording');
  }
  
  function updateLiveOutput(transcript) {
    const reference = document.getElementById('reference-text').textContent.replace(/[""]/g, '');
    const output = document.getElementById('live-output');
    output.textContent = transcript;
  
    const { wer, subs, dels, ins } = computeWER(reference, transcript);
    const wc = parseFloat(wer) < 15 ? 'var(--good)' : parseFloat(wer) < 30 ? 'var(--warn)' : 'var(--bad)';
  
    document.getElementById('live-wer-val').textContent = wer + '%';
    document.getElementById('live-wer-val').style.color = wc;
    document.getElementById('live-subs-val').textContent = subs;
    document.getElementById('live-dels-val').textContent = dels;
    document.getElementById('live-ins-val').textContent = ins;
  }
  
  /* Simulate demo if Web Speech API unavailable */
  function simulateLiveDemo() {
    isRecording = true;
    document.getElementById('mic-btn').classList.add('recording');
  
    const reference = 'The quick brown fox jumps over the lazy dog near the riverbank.';
    const imperfect = 'De quick brown fox jumps over de lazy dog near de riverbank.';
    const words = imperfect.split(' ');
  
    let out = '';
    let i = 0;
  
    const interval = setInterval(() => {
      if (i >= words.length) {
        clearInterval(interval);
        stopRecording();
        return;
      }
      out += (out ? ' ' : '') + words[i++];
      updateLiveOutput(out);
    }, 250);
  }
  
  /* ─── BOOT ───────────────────────────────────────────────────────────────────*/
  
  document.addEventListener('DOMContentLoaded', () => {
    init();
    renderErrorTypeChart();
    renderSystemRadar();
  });