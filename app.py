from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)  # للسماح للواجهة الأمامية بالاتصال بالبايثون دون قيود

@app.route('/analyze', methods=['POST'])
def analyze_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # قراءة الملف مباشرة من الذاكرة دون الحاجة لحفظه على السيرفر
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        df = pd.read_csv(stream)
        
        # معالجة وهيكلة البيانات بسرعة بايثون
        total_rows, total_cols = df.shape
        columns_list = list(df.columns)
        
        # استخراج الإحصائيات للأعمدة الرقمية تلقائياً
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        stats_summary = {}
        if numeric_cols:
            for col in numeric_cols:
                stats_summary[col] = {
                    'average': float(df[col].mean()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }

        # تجهيز أول 10 صفوف للمعاينة السريعة
        preview_data = df.head(10).to_dict(orient='records')

        # إرجاع النتيجة الكاملة للواجهة الأمامية
        return jsonify({
            'total_records': total_rows,
            'total_columns': total_cols,
            'columns': columns_list,
            'statistics': stats_summary,
            'preview': preview_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
