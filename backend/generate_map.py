"""
Generate an interactive Folium map for Tamil Nadu store locations.
This script creates an HTML file that can be embedded in the frontend.
"""
import folium
from folium.plugins import MarkerCluster

# Tamil Nadu center coordinates
TAMIL_NADU_CENTER = [10.8, 78.5]

# Store locations with real geographic coordinates
STORE_LOCATIONS = [
    {"id": "STORE_CHN", "name": "SK Brands - Chennai", "lat": 13.0827, "lon": 80.2707, "status": "medium"},
    {"id": "STORE_VLR", "name": "SK Brands - Vellore", "lat": 12.9184, "lon": 79.1325, "status": "low"},
    {"id": "STORE_SLM", "name": "SK Brands - Salem", "lat": 11.6512, "lon": 78.1587, "status": "medium"},
    {"id": "STORE_ERD", "name": "SK Brands - Erode", "lat": 11.3428, "lon": 77.7274, "status": "low"},
    {"id": "STORE_TPR", "name": "SK Brands - Tiruppur", "lat": 11.1154, "lon": 77.3546, "status": "medium"},
    {"id": "STORE_CBE", "name": "SK Brands - Coimbatore", "lat": 11.0056, "lon": 76.9661, "status": "low"},
    {"id": "STORE_TCH", "name": "SK Brands - Trichy", "lat": 10.8155, "lon": 78.6965, "status": "medium"},
    {"id": "STORE_TJV", "name": "SK Brands - Thanjavur", "lat": 10.7870, "lon": 79.1378, "status": "low"},
    {"id": "STORE_MDU", "name": "SK Brands - Madurai", "lat": 9.9190, "lon": 78.1195, "status": "critical"},
    {"id": "STORE_NGL", "name": "SK Brands - Nagercoil", "lat": 8.1780, "lon": 77.4120, "status": "low"},
]

# Status colors
STATUS_COLORS = {
    "critical": "red",
    "high": "orange", 
    "medium": "blue",
    "low": "green"
}

def create_tamil_nadu_map():
    """Create an interactive Folium map of Tamil Nadu with store markers."""
    
    # Create map centered on Tamil Nadu
    m = folium.Map(
        location=TAMIL_NADU_CENTER,
        zoom_start=7,
        tiles="CartoDB positron",
        scrollWheelZoom=True,
        dragging=True,
    )
    
    # Add store markers
    for store in STORE_LOCATIONS:
        color = STATUS_COLORS.get(store["status"], "blue")
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 150px;">
            <h4 style="margin: 0 0 8px 0; color: #1e293b;">{store['name']}</h4>
            <p style="margin: 0; color: #64748b; font-size: 12px;">ID: {store['id']}</p>
            <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">
                Status: <span style="color: {color}; font-weight: 600;">{store['status'].upper()}</span>
            </p>
        </div>
        """
        
        folium.CircleMarker(
            location=[store["lat"], store["lon"]],
            radius=6,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=store["name"],
            color="white",
            fill=True,
            fill_color="#3b82f6",
            fill_opacity=1,
            weight=3
        ).add_to(m)
    
    return m

def main():
    """Generate the map and save to frontend public folder."""
    print("Generating Tamil Nadu store map...")
    m = create_tamil_nadu_map()
    
    # Save to frontend public folder
    output_path = "../frontend/public/tamilnadu-stores-map.html"
    m.save(output_path)
    print(f"Map saved to: {output_path}")

if __name__ == "__main__":
    main()
