import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time
from typing import Dict, List, Tuple, Any
import logging

def analyze_time_patterns(schema: dict) -> Dict[str, Any]:
    """Analizza i pattern temporali nel database."""
    time_fields = []
    time_data = {}
    
    # Raccolta dati temporali
    for table_name, table in schema['tables'].items():
        for field_name, field in table['fields'].items():
            if (field.get('type', '').upper().startswith('TIME') or 
                field.get('category') == 'DateTime'):
                field_info = {
                    'table': table_name,
                    'field': field_name,
                    'examples': field.get('examples', []),
                    'type': field.get('type', ''),
                    'category': field.get('category', ''),
                }
                time_fields.append(field_info)
                
                # Organizza i dati per tipo di campo temporale
                field_key = f"{table_name}.{field_name}"
                time_data[field_key] = {
                    'values': field.get('examples', []),
                    'info': field_info
                }
    
    return analyze_time_distributions(time_data)

def analyze_time_distributions(time_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analizza la distribuzione dei valori temporali."""
    results = {
        'time_fields': len(time_data),
        'distributions': {},
        'patterns': [],
        'time_ranges': []
    }
    
    # Analisi per fasce orarie
    morning_fields = []
    afternoon_fields = []
    full_day_fields = []
    
    for field_key, data in time_data.items():
        times = []
        for val in data['values']:
            if isinstance(val, str):
                try:
                    # Converte stringe tempo in oggetti time
                    t = datetime.strptime(val, "%H:%M").time()
                    times.append(t)
                except ValueError:
                    continue
            elif isinstance(val, time):
                times.append(val)
        
        if not times:
            continue
            
        # Analizza la distribuzione oraria
        hour_dist = {}
        for t in times:
            hour = t.hour
            hour_dist[hour] = hour_dist.get(hour, 0) + 1
            
        results['distributions'][field_key] = hour_dist
        
        # Classifica il campo in base alla fascia oraria
        morning_hours = sum(1 for t in times if 5 <= t.hour < 12)
        afternoon_hours = sum(1 for t in times if 12 <= t.hour < 20)
        evening_hours = sum(1 for t in times if t.hour >= 20 or t.hour < 5)
        
        total_hours = len(times)
        if total_hours > 0:
            morning_ratio = morning_hours / total_hours
            afternoon_ratio = afternoon_hours / total_hours
            evening_ratio = evening_hours / total_hours
            
            if morning_ratio > 0.6:
                morning_fields.append(field_key)
            elif afternoon_ratio > 0.6:
                afternoon_fields.append(field_key)
            else:
                full_day_fields.append(field_key)
                
            # Identifica range temporali
            if times:
                min_time = min(times)
                max_time = max(times)
                results['time_ranges'].append({
                    'field': field_key,
                    'min_time': min_time.strftime('%H:%M'),
                    'max_time': max_time.strftime('%H:%M')
                })
    
    # Identifica pattern comuni
    if len(morning_fields) > 0:
        results['patterns'].append({
            'type': 'morning',
            'fields': morning_fields,
            'description': 'Campi con orari prevalentemente mattutini (5-12)'
        })
    
    if len(afternoon_fields) > 0:
        results['patterns'].append({
            'type': 'afternoon',
            'fields': afternoon_fields,
            'description': 'Campi con orari prevalentemente pomeridiani (12-20)'
        })
    
    if len(full_day_fields) > 0:
        results['patterns'].append({
            'type': 'full_day',
            'fields': full_day_fields,
            'description': 'Campi con orari distribuiti su tutto il giorno'
        })
    
    return results

def create_time_visualizations(time_analysis: Dict[str, Any], output_dir: str) -> List[str]:
    """Crea visualizzazioni per i pattern temporali."""
    plots = []
    
    # 1. Distribuzione oraria per campo
    distributions = time_analysis['distributions']
    if distributions:
        fig = make_subplots(
            rows=len(distributions), 
            cols=1,
            subplot_titles=list(distributions.keys()),
            vertical_spacing=0.05
        )
        
        for i, (field, dist) in enumerate(distributions.items(), 1):
            hours = list(range(24))
            counts = [dist.get(h, 0) for h in hours]
            
            fig.add_trace(
                go.Bar(x=hours, y=counts, name=field),
                row=i, col=1
            )
            
            fig.update_xaxes(title_text="Ora del giorno", row=i, col=1)
            fig.update_yaxes(title_text="Conteggio", row=i, col=1)
        
        fig.update_layout(
            height=300 * len(distributions),
            title_text="Distribuzione Oraria per Campo Temporale",
            showlegend=False
        )
        
        plot_path = f"{output_dir}/time_distributions.html"
        fig.write_html(plot_path)
        plots.append(plot_path)
    
    # 2. Heatmap delle fasce orarie
    if distributions:
        all_hours = range(24)
        all_fields = list(distributions.keys())
        
        heatmap_data = []
        for field in all_fields:
            dist = distributions[field]
            row = [dist.get(hour, 0) for hour in all_hours]
            heatmap_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=list(all_hours),
            y=all_fields,
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title='Heatmap delle Fasce Orarie',
            xaxis_title='Ora del giorno',
            yaxis_title='Campo',
            height=max(400, 50 * len(all_fields))
        )
        
        plot_path = f"{output_dir}/time_heatmap.html"
        fig.write_html(plot_path)
        plots.append(plot_path)
    
    # 3. Range temporali
    if time_analysis['time_ranges']:
        fig = go.Figure()
        
        for range_info in time_analysis['time_ranges']:
            field = range_info['field']
            min_time = datetime.strptime(range_info['min_time'], '%H:%M')
            max_time = datetime.strptime(range_info['max_time'], '%H:%M')
            
            fig.add_trace(go.Scatter(
                x=[min_time.hour + min_time.minute/60, 
                   max_time.hour + max_time.minute/60],
                y=[field, field],
                mode='lines+markers',
                name=field,
                line=dict(width=8)
            ))
        
        fig.update_layout(
            title='Range Temporali per Campo',
            xaxis_title='Ora del giorno',
            yaxis_title='Campo',
            height=max(400, 50 * len(time_analysis['time_ranges'])),
            showlegend=False
        )
        
        plot_path = f"{output_dir}/time_ranges.html"
        fig.write_html(plot_path)
        plots.append(plot_path)
    
    return plots

def generate_time_patterns_section(time_analysis: Dict[str, Any]) -> str:
    """Genera la sezione HTML per i pattern temporali."""
    html = """
    <div class="section">
        <h2>Analisi Pattern Temporali</h2>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Campi Temporali</h3>
                <p>{}</p>
            </div>
        </div>
        
        <h3>Pattern Identificati</h3>
        <div class="patterns">
    """.format(time_analysis['time_fields'])
    
    for pattern in time_analysis['patterns']:
        html += """
            <div class="pattern-card">
                <h4>{}</h4>
                <p>{}</p>
                <ul>
        """.format(pattern['type'].title(), pattern['description'])
        
        for field in pattern['fields']:
            html += f"<li>{field}</li>"
        
        html += """
                </ul>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html