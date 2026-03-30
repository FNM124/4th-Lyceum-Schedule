import requests
import pdfplumber
import io
import re
import json
from datetime import datetime

# --- CONFIGURATION ---
URL = "https://sites.google.com/view/program-4lyk-ilioup/"
# Add any class you want the website to track here!
SCHOOL_CLASSES = ["Α1", "Α2", "Α3", "Α4", "Β1", "Β2", "Β3", "Β4", "ΒΘ1", "ΒΘ2", "ΒΑΝ1", "ΒΑΝ2", "Γ1", "Γ2", "Γ3", "Γ4", "ΓΘ1", "ΓΘ2", "ΓΟ1", "ΓΟ2", "ΓΑΝ1", "ΓΑΝ2", "ΓΥΓ1", "ΓΥΓ2"]

def clean_text(text):
    """Accurate Greek normalization to prevent mismatch errors."""
    if not text: return ""
    text = str(text).strip().upper()
    replacements = {
        'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ώ': 'Ω',
        'Ϊ': 'Ι', 'Ϋ': 'Υ', 'ΐ': 'Ι', 'ΰ': 'Υ'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^\w\s]', '', text)
    return text.replace(" ", "")

def update_web_html(schedule_data_dict, target_day):
    """Generates the HTML file with LocalStorage Memory and Dropdown."""
    current_year = datetime.now().year
    
    # We turn the Python dictionary into a JavaScript object
    json_data = json.dumps(schedule_data_dict, ensure_ascii=False)
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="el">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>School Schedule</title>
        <style>
            body {{ background: #050505; color: #fff; font-family: 'Inter', sans-serif; padding: 20px; display: flex; justify-content: center; }}
            .card {{ background: #111; border: 1px solid #333; border-radius: 12px; width: 100%; max-width: 450px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #00ff41; padding-bottom: 10px; }}
            .day-name {{ font-size: 1.4rem; font-weight: 800; text-transform: uppercase; color: #00ff41; }}
            
            .row {{ display: flex; align-items: center; padding: 12px; border-bottom: 1px solid #222; }}
            .row:last-child {{ border-bottom: none; }}
            .hour-circle {{ width: 35px; height: 35px; border-radius: 50%; border: 1px solid #00ff41; display: flex; justify-content: center; align-items: center; margin-right: 15px; font-weight: bold; font-family: monospace; color: #00ff41; flex-shrink: 0; }}
            .details {{ flex-grow: 1; font-size: 1rem; color: #eee; }}
            .empty {{ color: #444; font-style: italic; }}
            
            /* The New Dropdown Controls */
            .controls {{ margin-top: 15px; border-top: 1px solid #222; padding-top: 15px; display: flex; align-items: center; }}
            .controls label {{ font-size: 0.7rem; color: #888; letter-spacing: 1px; font-weight: bold; }}
            select {{ background: #1a1a1a; color: #00ff41; border: 1px solid #333; padding: 6px 12px; border-radius: 6px; font-family: 'Inter', sans-serif; font-weight: bold; outline: none; margin-left: 10px; cursor: pointer; }}
            select:focus {{ border-color: #00ff41; }}
            
            .sync-info {{ text-align: center; margin-top: 20px; font-size: 0.6rem; color: #444; letter-spacing: 1px; }}
            .copyright {{ text-align: center; margin-top: 5px; font-size: 0.6rem; color: #222; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <span class="day-name">{target_day}</span>
                <span id="display-class-name" style="font-size: 0.9rem; color: #666; font-weight: bold;"></span>
            </div>
            
            <div id="list"></div>
            
            <div class="controls">
                <label for="class-select">CLASS:</label>
                <select id="class-select"></select>
            </div>
            
            <div class="sync-info">LAST_REFRESH: {datetime.now().strftime('%H:%M:%S')}</div>
            <div class="copyright">© FNM124 {current_year} All rights reserved.</div>
        </div>

        <script>
            const allData = {json_data};
            const container = document.getElementById('list');
            const select = document.getElementById('class-select');
            const classTitle = document.getElementById('display-class-name');
            
            // 1. Fill the dropdown with available classes
            const availableClasses = Object.keys(allData).sort();
            availableClasses.forEach(c => {{
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                select.appendChild(opt);
            }});

            // 2. Memory Check: Load saved class, default to B3 if empty
            let currentClass = localStorage.getItem('fnm_user_class');
            if (!currentClass || !availableClasses.includes(currentClass)) {{
                currentClass = availableClasses.includes('Β3') ? 'Β3' : availableClasses[0];
            }}
            select.value = currentClass;

            // 3. Engine to draw the table
            function renderSchedule(className) {{
                container.innerHTML = '';
                classTitle.textContent = className; // Update top right text
                
                const hours = allData[className] || ["", "", "", "", "", "", ""];
                
                hours.forEach((teacher, index) => {{
                    const num = index + 1;
                    const text = teacher ? teacher.trim() : "";
                    
                    const div = document.createElement('div');
                    div.className = 'row';
                    div.innerHTML = `<div class="hour-circle">${{num}}</div><div class="details ${{text ? '' : 'empty'}}">${{text || 'No Class'}}</div>`;
                    container.appendChild(div);
                }});
            }}

            // 4. Draw it the first time
            renderSchedule(currentClass);

            // 5. Listen for user changing the dropdown
            select.addEventListener('change', (e) => {{
                const selected = e.target.value;
                localStorage.setItem('fnm_user_class', selected); // Save to memory!
                renderSchedule(selected); // Redraw instantly
            }});
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def run_scraper():
    days_gr = ["ΔΕΥΤΕΡΑ", "ΤΡΙΤΗ", "ΤΕΤΑΡΤΗ", "ΠΕΜΠΤΗ", "ΠΑΡΑΣΚΕΥΗ", "ΣΑΒΒΑΤΟ", "ΚΥΡΙΑΚΗ"]
    now = datetime.now()
    today_idx = now.weekday()
    target_idx = 0 if today_idx >= 4 else today_idx + 1
    target_day = days_gr[target_idx]
    
    print(f"Status: Verifying PDF for {target_day}...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        raw_text = requests.get(URL, headers=headers).text.replace('\\/', '/')
        file_id = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]{25,})', raw_text).group(1)
        pdf_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        pdf_data = requests.get(pdf_url).content
        
        found_column = -1

        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            table = pdf.pages[0].extract_table()
            
            target_clean = clean_text(target_day)
            for r_idx, row in enumerate(table[:5]): 
                if not row: continue
                for c_idx, cell in enumerate(row):
                    if cell and target_clean in clean_text(cell):
                        found_column = c_idx
                        break
                if found_column != -1: break

            if found_column == -1:
                # If day isn't found, pass empty dictionary so site doesn't crash
                update_web_html({}, target_day)
                raise ValueError(f"SYSTEM_ERROR: Could not find header '{target_day}'.")

            # --- THE NEW UNIVERSAL SEARCH LOGIC ---
            # Create empty 7-hour arrays for every class
            all_schedules = {c: [""] * 7 for c in SCHOOL_CLASSES}
            ongoing_classes = {} # Tracks merged cells for each row
            
            for h in range(7):
                col_idx = found_column + h
                
                for r_idx, row in enumerate(table[2:]):
                    # Clean the teacher's name (Don't use clean_text here, we want spaces!)
                    teacher = str(row[0]).strip() if row[0] else ""
                    
                    raw_cell = row[col_idx] if len(row) > col_idx else "" 
                    cell_str = str(raw_cell).strip().upper().replace(" ", "") if raw_cell is not None else ""
                    
                    if raw_cell is not None and cell_str != "":
                        # Look for any of our classes in this cell
                        found_in_cell = []
                        for c in SCHOOL_CLASSES:
                            if c in cell_str:
                                found_in_cell.append(c)
                        
                        ongoing_classes[r_idx] = found_in_cell
                        
                        for c in found_in_cell:
                            all_schedules[c][h] = teacher
                            
                    elif raw_cell is None:
                        # Merged cell shadow! Carry over from the previous hour
                        carried_over = ongoing_classes.get(r_idx, [])
                        for c in carried_over:
                            # Only assign if it's currently empty
                            if not all_schedules[c][h] and teacher:
                                all_schedules[c][h] = teacher
                    else:
                        ongoing_classes[r_idx] = []

        # Remove classes that have NO teachers all day to keep the dropdown clean
        clean_schedules = {k: v for k, v in all_schedules.items() if any(v)}
        
        # Save raw JSON data to professors.txt just in case you need to debug
        with open("professors.txt", "w", encoding="utf-8") as f:
            json.dump(clean_schedules, f, ensure_ascii=False, indent=4)
            
        update_web_html(clean_schedules, target_day)

    except Exception as e:
        error_msg = f"System Error: {e}"
        with open("professors.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        update_web_html({}, "ERROR")

if __name__ == "__main__":
    run_scraper()
