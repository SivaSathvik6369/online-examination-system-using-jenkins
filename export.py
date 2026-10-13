def export_results_to_csv(results, filepath):
    with open(filepath, 'w') as f:
        f.write('student,email,score,status\n')
        for r in results:
            f.write(f\"{r['name']},{r.get('email','')},{r['score']},{r['passed']}\n\")
