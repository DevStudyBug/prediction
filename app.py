from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        # Fall back to static file if template doesn't exist
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, 'index.html')
        
        if os.path.exists(html_path):
            with open(html_path, 'r') as file:
                return file.read()
        else:
            return f"Error: Could not find index.html. Error: {str(e)}", 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        data = request.form.to_dict()
        print("Received data:", data)
        
        # Check for KT in progress (business rule)
        if data.get('kt_status') == 'KT In Progress':
            result = 'Not Eligible for Placement'
            recommendation = 'Employee must complete KT before being considered for placement.'
            return render_template('index.html', result=result, recommendation=recommendation)
        
        # Convert string values to appropriate numerical types
        ssc_p = float(data.get('ssc_p', 0))
        hsc_p = float(data.get('hsc_p', 0))
        degree_p = float(data.get('degree_p', 0))
        etest_p = float(data.get('etest_p', 0))
        mba_p = float(data.get('mba_p', 0) or 0)
        
        # Simple prediction logic without numpy or pandas
        workex = data.get('workex', 'No')
        kt_status = data.get('kt_status', 'No KT')
        
        # Calculate a simple score
        score = (
            (ssc_p / 100) * 0.1 +
            (hsc_p / 100) * 0.1 +
            (degree_p / 100) * 0.3 +
            (etest_p / 100) * 0.3 +
            (mba_p / 100) * 0.1 +
            (1 if workex == 'Yes' else 0) * 0.1
        )
        
        # Adjust for KT status
        if kt_status == 'KT Completed':
            score *= 0.9
        
        # Determine prediction and confidence
        confidence = score * 100
        if score > 0.6:
            prediction = 'Placed'
        else:
            prediction = 'Not Placed'
            confidence = (1 - score) * 100
        
        # Generate result text and recommendation
        if prediction == 'Placed':
            result = f'Likely to be Placed (Confidence: {confidence:.1f}%)'
            
            if degree_p < 60:
                recommendation = 'Consider courses to improve academic performance.'
            elif etest_p < 70:
                recommendation = 'Focus on employability skills to increase placement chances.'
            elif workex == 'No':
                recommendation = 'Adding relevant work experience could further improve placement chances.'
            else:
                recommendation = 'Strong profile with good placement potential. Ready for job interviews.'
        else:
            result = f'May Not be Placed (Confidence: {confidence:.1f}%)'
            
            areas_to_improve = []
            if degree_p < 70:
                areas_to_improve.append('degree percentage')
            if etest_p < 75:
                areas_to_improve.append('employability test scores')
            if workex == 'No':
                areas_to_improve.append('practical work experience')
                
            if areas_to_improve:
                recommendation = f'Focus on improving: {", ".join(areas_to_improve)}.'
            else:
                recommendation = 'Consider additional certifications or projects to stand out.'
        
        print("Prediction result:", result)
        print("Recommendation:", recommendation)
        
        # Return template with prediction result
        return render_template('index.html', result=result, recommendation=recommendation)
    
    except Exception as e:
        import traceback
        print(f"Error in prediction: {str(e)}")
        print(traceback.format_exc())
        error_message = f'An error occurred: {str(e)}. Please check your input data and try again.'
        return render_template('index.html', result='Error in Prediction', recommendation=error_message)

if __name__ == '__main__':
    import os
    # Check needed directories exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
        # Move index.html to templates if it exists in current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(current_dir, 'index.html')
        dest_path = os.path.join(current_dir, 'templates', 'index.html')
        
        if os.path.exists(src_path) and not os.path.exists(dest_path):
            import shutil
            shutil.copy2(src_path, dest_path)
            print(f"Copied index.html to templates directory")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)