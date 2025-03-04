import networkx as nx
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

COLOR_MAP = {
    'Intern': px.colors.qualitative.Set1[3],      
    'Entry Level': px.colors.qualitative.Set1[2], 
    'Mid-Level': px.colors.qualitative.Set1[1],    
    'Senior-Level': px.colors.qualitative.Set1[0],
    'Leadership': px.colors.qualitative.Set1[4]
}
CATEGORY_ORDER = ['Intern', 'Entry Level', 'Mid-Level', 'Senior-Level', 'Leadership']

def create_seniority_plot(jobs_per_month_by_seniority):
    
    selected_seniority = ['Senior-Level, us', 'Senior-Level, canada', 
                          'Entry Level, us', 'Entry Level, canada', 
                          'Mid-Level, us', 'Mid-Level, canada',
                          'Intern, us', 'Intern, canada',
                          # 'Leadership, canada', 'Leadership, us'
                         ]

    line_style_mapping = {
        'us': 'solid',
        'canada': 'dashdot'
    }


    fig = px.line(
        jobs_per_month_by_seniority,
        x='year_month',           
        y='smoothed_value',  
        color='binned_seniority',  
        line_dash='country',      
        facet_col='job_category',  
        line_group='binned_seniority',  
        markers=False,     
        facet_col_wrap=5,   
        color_discrete_map=COLOR_MAP,
        category_orders={
            'binned_seniority': CATEGORY_ORDER
        }  
    )

    for trace in fig.data:
        country_name = trace.name.split(", ")[-1] 
        if country_name in line_style_mapping:
            trace.line.dash = line_style_mapping[country_name] 

    fig.add_vline(
        x=pd.Timestamp("2024-06-27"),  
        line_width=1,
        line_dash="dash",
        line_color="red",
        opacity = 0.8
    )
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[1]))    
    fig.update_traces(marker=dict(line=dict( width=0.8, color='white')))
    fig.update_layout(
        legend_title='Seniority Level',
        height=350,  
        width=1200,   
        legend=dict(
            orientation='h',   
            yanchor='bottom',   
            y=1.10,            
            xanchor='center',   
            x=0.5              
        )
    )
    
    for axis in fig.layout:
        if axis.startswith('xaxis'):  
            fig.update_layout({axis: dict(
                tickangle=45,        
                title='Year-Month',
                tickmode='linear',  
                dtick='M2'           
            )})
        # if axis in ['yaxis', 'yaxis6']:
        #     fig.update_layout({axis: dict(
        #         title=f"{by.title()} Normalized Salary (USD)"  
        #     )})
    
    
    for trace in fig.data:
        if trace.name in selected_seniority:
            trace.visible = True 
        else:
            trace.visible = 'legendonly' 

    return fig 


def create_salary_plot(filtered_jobs):

    selected_seniority = ['Senior-Level, us', 'Senior-Level, canada', 
                          'Entry Level, us', 'Entry Level, canada', 
                          'Mid-Level, us', 'Mid-Level, canada',
                          'Intern, us', 'Intern, canada',
                          # 'Leadership, canada', 'Leadership, us'
                         ]

    line_style_mapping = {
        'us': 'solid',
        'canada': 'dashdot'
    }



    fig = px.line(
        filtered_jobs,
        x='year_month',           
        y='smoothed_value',  
        color='binned_seniority',  
        line_dash='country',      
        facet_col='job_category',  
        line_group='binned_seniority',  
        markers=False,     
        facet_col_wrap=5,   
        color_discrete_map=COLOR_MAP,
        category_orders={
            'binned_seniority': CATEGORY_ORDER
        }      
    )
    for trace in fig.data:
        country_name = trace.name.split(", ")[-1]  
        if country_name in line_style_mapping:
            trace.line.dash = line_style_mapping[country_name]  

    fig.add_vline(
        x=pd.Timestamp("2024-06-27"),  
        line_width=1,
        line_dash="dash",
        line_color="red",
        opacity = 0.8
    )


    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[1]))    
    fig.update_traces(marker=dict(line=dict( width=0.8, color='white')))
    fig.update_layout(
        legend_title='Seniority Level',
        height=350,  
        width=1200,   
        legend=dict(
            orientation='h',   
            yanchor='bottom',   
            y=1.10,            
            xanchor='center',   
            x=0.5              
        )
    )

    for axis in fig.layout:
        if axis.startswith('xaxis'):  
            fig.update_layout({axis: dict(
                tickangle=45,        
                title='Year-Month',
                tickmode='linear',  
                dtick='M2'           
            )})
        if axis in ['yaxis', 'yaxis6']:
            fig.update_layout({axis: dict(
                title="Normalized Salary (USD)"  
            )})

    for trace in fig.data:
        if trace.name in selected_seniority:
            trace.visible = True 
        else:
            trace.visible = 'legendonly' 

    return fig



def create_skill_heatmap(df, height = 600, width = 600):

    tech_sums = df.drop(columns=['job_category', 'year_month', 'total_jobs']).sum().sort_values(ascending=False)

    # tech_sums = df.drop(columns=['year_month', 'total_jobs']).sum().sort_values(ascending=False)
    df = df[['year_month'] + tech_sums.index.tolist() + ['total_jobs']]

    # treat time purely as string so plotly doesn't interpret it linearly, which widens some cells
    # df['year_month'] = df['year_month'].astype(str)
    df['year_month'] = pd.to_datetime(df['year_month']).dt.strftime('%B %Y')
    # df['year_month'] = pd.to_datetime(df['year_month'].astype(str), format='%Y-%m')

    total_jobs_per_month = df[['total_jobs', 'year_month']].drop_duplicates()
    total_jobs_per_month.set_index('year_month', inplace=True)
    df.set_index('year_month', inplace=True)

    heatmap_data = df.drop(columns='total_jobs')


    fig = px.imshow(
        heatmap_data.T,                                                      # transpose the data so technologies are on the y-axis
        labels=dict(x="Year-Month", y="Technology", color="Proportion"),
        y=heatmap_data.columns,                                              # technologies
        x=heatmap_data.index,                                                # year-Month
        aspect="auto",
        text_auto=True,
        color_continuous_scale='Inferno_r',
    )

    # total jobs data on the secondary x-axis
    fig.add_trace(
        go.Scatter(
            x=total_jobs_per_month.index,
            # y = 0,
            y=[0] * len(total_jobs_per_month),  # adjust this value to position above the heatmap
            text=total_jobs_per_month['total_jobs'],
            mode="text",
            showlegend=False,
            xaxis="x2"
        )
    )


    fig.update_layout(
        height = height,
        width = width,
        yaxis=dict(
            tickmode='linear',  
            tickvals=list(range(len(heatmap_data.columns))),
            ticktext=heatmap_data.columns.tolist(),
            nticks=len(heatmap_data.columns),  
            showticklabels=True, 
        ),
        xaxis=dict(
            tickangle=45,
            type = "category",
            side = "bottom"
        ),
        xaxis2=dict(
            type = "category",
            overlaying="x",
            side="bottom",
            showticklabels=False,
            tickmode='array',
            tickvals=[i for i in range(len(total_jobs_per_month.index))],
            ticktext=total_jobs_per_month.index.tolist()
        ),
    )

    

    return fig 

def create_network_graph(category, filtered_pairs, dates_for_title, layout_algo, k=20, edge_scaling_factor=0.1, normalize=True, height=600):

    G = nx.Graph()
    
    # add edges to the graph with weights as the frequency of co-occurrence
    # for pair, weight in filtered_pairs.items():
    #     G.add_edge(pair[0], pair[1], weight=weight)
    
    # 'filtered_pairs' is a list of {"pair": [...], "count": ...}
    # add edges to the graph with weights as the frequency of co-occurrence
    for item in filtered_pairs:
        pair = item["pair"]          # e.g., ["aws","git"]
        weight = item["count"]
        G.add_edge(pair[0], pair[1], weight=weight)

    if normalize:
        max_weight = max(nx.get_edge_attributes(G, 'weight').values()) if G.edges else 1 
        for edge in G.edges(data=True):
            edge[2]['weight'] /= max_weight
    
    if layout_algo == 'Spring Layout':
        pos = nx.spring_layout(G, k=k)
    elif layout_algo == 'Circular Layout':
        pos = nx.circular_layout(G)
    elif layout_algo == 'Kamada-Kawai Layout':
        pos = nx.kamada_kawai_layout(G)
    elif layout_algo == 'Spectral Layout':
        pos = nx.spectral_layout(G)
    elif layout_algo == 'Shell Layout':
        pos = nx.shell_layout(G)

    # create edges with color and thickness based on weight
    edge_traces = []
    for edge in G.edges(data=True):
        node1, node2, edge_attr = edge
        x0, y0 = pos[node1]
        x1, y1 = pos[node2]
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=edge_attr['weight'] * edge_scaling_factor, color='black'),
            hoverinfo='none',
            mode='lines',
            name='Edges'))

    # create nodes with size based on degree
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,    # keep rest of arguments in case we want this back
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=[],
            line_width=2),
        name='Nodes')

    # color nodes by degree (number of connections)
    node_adjacencies = []
    node_text = []
    for node, adjacencies in G.adjacency():
        node_adjacencies.append(len(adjacencies))
        node_text.append(f'{node}<br>: {len(adjacencies)}')

    # size nodes based on degree
    node_trace.marker.size = [1 + adjacencies * 1.5 for adjacencies in node_adjacencies]
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    # create labels as a separate trace to overlay on top
    label_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='text',
        text=[f'{node}' for node in G.nodes()],
        textposition="bottom center", 
        textfont=dict(size=12, color='black', family='Arial'),
        # hoverinfo='none',  
        name='Labels'
    )
    fig = go.Figure(data=edge_traces + [node_trace, label_trace],  
                    layout=go.Layout(
                                  title=f'{category} - {dates_for_title}',
                        # titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        autosize=True,
                        height=height,
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(showarrow=False, xref="paper", yref="paper")],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        paper_bgcolor='white',
                        plot_bgcolor='white'))

    return fig