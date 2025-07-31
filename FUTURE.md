# Future Use Cases for broflow

## ParallelAction Use Cases

### 1. Feature Engineering in Machine Learning
Perfect for independent feature computations that can run simultaneously.

```python
from broflow import Action, Flow, Start, End
from broflow.parallel_action import ParallelAction

class ScaleFeature(Action):
    def run(self, shared):
        df = shared['data']
        return (df['price'] - df['price'].mean()) / df['price'].std()

class LogTransform(Action):
    def run(self, shared):
        df = shared['data']
        return np.log1p(df['sales'])

class OneHotEncode(Action):
    def run(self, shared):
        df = shared['data']
        return pd.get_dummies(df['category'])

class FeatureMerger(Action):
    def run(self, shared):
        features = shared['parallel']
        merged_df = pd.concat([
            shared['data'],
            pd.DataFrame({'scaled_price': features['scalefeature']}),
            pd.DataFrame({'log_sales': features['logtransform']}),
            features['onehotencode']
        ], axis=1)
        shared['engineered_data'] = merged_df
        return shared

# Build ML feature pipeline
start = Start("Feature engineering pipeline")
feature_parallel = ParallelAction(ScaleFeature(), LogTransform(), OneHotEncode())
merger = FeatureMerger()
end = End("Features ready")

start >> feature_parallel >> merger >> end
flow = Flow(start)
flow.run({'data': raw_dataframe})
```

### 2. Multi-Source Data Fetching
Ideal for gathering data from multiple sources simultaneously.

```python
class DatabaseFetcher(Action):
    def run(self, shared):
        conn = get_db_connection()
        return conn.execute("SELECT * FROM users WHERE id = ?", shared['user_id']).fetchall()

class APIFetcher(Action):
    def run(self, shared):
        response = requests.get(f"https://api.service.com/user/{shared['user_id']}")
        return response.json()

class FileFetcher(Action):
    def run(self, shared):
        with open(f"data/{shared['user_id']}.json") as f:
            return json.load(f)

class DataMerger(Action):
    def run(self, shared):
        results = shared['parallel']
        merged = {
            'profile': results['databasefetcher'],
            'preferences': results['apifetcher'],
            'history': results['filefetcher']
        }
        shared['user_data'] = merged
        return shared

# Multi-source data pipeline
start = Start("Fetching user data")
data_fetcher = ParallelAction(DatabaseFetcher(), APIFetcher(), FileFetcher())
merger = DataMerger()
end = End("Data merged")

start >> data_fetcher >> merger >> end
```

### 3. Web Scraping Multiple Sites
Perfect for concurrent web scraping with natural parallelism.

```python
class AmazonScraper(Action):
    def run(self, shared):
        response = requests.get(f"https://amazon.com/product/{shared['product_id']}")
        return {'price': parse_amazon_price(response.text), 'availability': True}

class EbayScraper(Action):
    def run(self, shared):
        response = requests.get(f"https://ebay.com/item/{shared['product_id']}")
        return {'price': parse_ebay_price(response.text), 'availability': True}

class WalmartScraper(Action):
    def run(self, shared):
        response = requests.get(f"https://walmart.com/ip/{shared['product_id']}")
        return {'price': parse_walmart_price(response.text), 'availability': False}

class PriceComparator(Action):
    def run(self, shared):
        results = shared['parallel']
        prices = [r['price'] for r in results.values() if r and r['availability']]
        shared['best_price'] = min(prices) if prices else None
        shared['price_comparison'] = results
        return shared

# Price comparison pipeline
start = Start("Price comparison scraping")
scrapers = ParallelAction(AmazonScraper(), EbayScraper(), WalmartScraper())
comparator = PriceComparator()
end = End("Price comparison complete")

start >> scrapers >> comparator >> end
```

### 4. Parallel Processing Workflows
For CPU-intensive tasks that can be parallelized.

```python
class ImageProcessor(Action):
    def __init__(self, filter_type):
        super().__init__()
        self.filter_type = filter_type
    
    def run(self, shared):
        image = shared['image']
        if self.filter_type == 'blur':
            return cv2.GaussianBlur(image, (15, 15), 0)
        elif self.filter_type == 'sharpen':
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            return cv2.filter2D(image, -1, kernel)
        elif self.filter_type == 'edge':
            return cv2.Canny(image, 100, 200)

class ImageMerger(Action):
    def run(self, shared):
        results = shared['parallel']
        shared['processed_images'] = {
            'blur': results['imageprocessor'],  # First instance
            'sharpen': results.get('imageprocessor_1'),  # Need better naming
            'edge': results.get('imageprocessor_2')
        }
        return shared

# Image processing pipeline
start = Start("Image processing")
processors = ParallelAction(
    ImageProcessor('blur'),
    ImageProcessor('sharpen'), 
    ImageProcessor('edge')
)
merger = ImageMerger()
end = End("Images processed")

start >> processors >> merger >> end
```

### 5. Notification Systems
Send notifications through multiple channels simultaneously.

```python
class EmailNotifier(Action):
    def run(self, shared):
        send_email(shared['recipient'], shared['message'])
        return {'email_sent': True, 'timestamp': datetime.now()}

class SMSNotifier(Action):
    def run(self, shared):
        send_sms(shared['phone'], shared['message'])
        return {'sms_sent': True, 'timestamp': datetime.now()}

class PushNotifier(Action):
    def run(self, shared):
        send_push(shared['device_id'], shared['message'])
        return {'push_sent': True, 'timestamp': datetime.now()}

class NotificationLogger(Action):
    def run(self, shared):
        results = shared['parallel']
        success_count = sum(1 for r in results.values() if r and r.get('email_sent') or r.get('sms_sent') or r.get('push_sent'))
        shared['notification_summary'] = f"{success_count} notifications sent successfully"
        return shared

# Multi-channel notification pipeline
start = Start("Sending notifications")
notifiers = ParallelAction(EmailNotifier(), SMSNotifier(), PushNotifier())
logger = NotificationLogger()
end = End("Notifications complete")

start >> notifiers >> logger >> end
```

## Advanced Patterns

### Conditional ParallelAction
```python
class ConditionalParallelAction(Action):
    def __init__(self, condition_key, action_map):
        super().__init__()
        self.condition_key = condition_key
        self.action_map = action_map
    
    def run(self, shared):
        condition = shared.get(self.condition_key)
        actions = self.action_map.get(condition, [])
        
        if actions:
            parallel = ParallelAction(*actions)
            return parallel.run(shared)
        return shared

# Usage
conditional_parallel = ConditionalParallelAction('user_type', {
    'premium': [EmailNotifier(), SMSNotifier(), PushNotifier()],
    'basic': [EmailNotifier()],
    'free': []
})
```

### Batched ParallelAction
```python
class BatchedParallelAction(Action):
    def __init__(self, action_class, batch_size=10):
        super().__init__()
        self.action_class = action_class
        self.batch_size = batch_size
    
    def run(self, shared):
        items = shared.get('items', [])
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            actions = [self.action_class() for _ in batch]
            
            # Process batch in parallel
            batch_shared = shared.copy()
            batch_shared['batch_items'] = batch
            
            parallel = ParallelAction(*actions)
            batch_result = parallel.run(batch_shared)
            results.extend(batch_result['parallel'].values())
        
        shared['batch_results'] = results
        return shared
```

## Performance Considerations

### When to Use ParallelAction
- ✅ I/O-bound operations (network, file, database)
- ✅ Independent computations
- ✅ Tasks taking >100ms each
- ✅ Multiple data sources
- ✅ Feature engineering

### When NOT to Use ParallelAction
- ❌ CPU-bound tasks (use multiprocessing)
- ❌ Fast operations (<10ms)
- ❌ Shared mutable resources
- ❌ Sequential dependencies
- ❌ Memory-intensive operations

### Best Practices
1. **Limit concurrency** for resource-intensive operations
2. **Handle exceptions** gracefully in each action
3. **Use meaningful result keys** for easier debugging
4. **Copy shared state** when needed to avoid race conditions
5. **Monitor resource usage** (memory, connections, threads)