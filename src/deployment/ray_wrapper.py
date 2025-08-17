import yaml
import ray
from ray import serve
import uuid
from typing import Type, Any

with open("deployment_config.yml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


class RayDeployment:
    def __init__(self, model_class: Type[Any], stage="development", deployment_decorator=None):
        """
        Initialize RayDeployment with a model class
        
        Args:
            model_class: The model class to deploy
            stage: Deployment stage (development, testing, production)
        """
        if stage not in config["allowed_stages"]:
            raise ValueError(f'Stage {stage} not allowed, allowed stages are {config["allowed_stages"]}')
        
        self.model_class = model_class
        self.stage = stage
        self.deployment_decorator = deployment_decorator
        self.deployment_id = str(uuid.uuid4())[:8]  # Generate unique ID
        self.deployment_name = f"{model_class.__name__}_{self.deployment_id}"

        
    def deploy_model(self):
        """Deploy the model using Ray Serve"""
        if not ray.is_initialized():
            ray.init()  # Start ray if it's not started already
        
        # Start Ray Serve
        serve.start(detached=True)
        
        # Create Ray Serve deployment decorator with appropriate settings
        if self.deployment_decorator is not None:
            deployment_decorator = serve.deployment(self.deployment_decorator)
        elif self.stage == "production":
            deployment_decorator = serve.deployment(
                name=self.deployment_name,
                num_replicas=config["production_settings"]["num_replicas"],
                ray_actor_options={
                    "num_cpus": config["default_resources"]["num_cpus"],
                    "num_gpus": config["default_resources"]["num_gpus"],
                    "memory": config["default_resources"]["memory"]
                },
                health_check_timeout_s=config["production_settings"]["health_check_timeout_s"],
                graceful_shutdown_wait_loop_s=config["production_settings"]["graceful_shutdown_wait_loop_s"]
            )
        else:
            # Development/testing settings
            deployment_decorator = serve.deployment(
                name=self.deployment_name,
                num_replicas=1,
                ray_actor_options={
                    "num_cpus": config["default_resources"]["num_cpus"],
                    "num_gpus": config["default_resources"]["num_gpus"],
                    "memory": config["default_resources"]["memory"]
                }
            )
        
        # Create the deployment class
        @deployment_decorator
        class ModelDeployment:
            def __init__(self):
                self.model_instance = self.model_class()
            
            async def __call__(self, request):
                """Handle HTTP requests"""
                try:
                    # Get text from request
                    if hasattr(request, 'query_params'):
                        # Query parameter approach
                        text = request.query_params.get("text", "")
                    else:
                        # JSON body approach
                        import json
                        body = await request.body()
                        data = json.loads(body)
                        text = data.get("text", "")
                    
                    if not text:
                        return {"error": "No text provided. Use ?text=your_text or send JSON with 'text' field"}
                    
                    # Use the model's classify_text method
                    if hasattr(self.model_instance, 'classify_text'):
                        result = self.model_instance.classify_text(text)
                        return {
                            "text": text,
                            "predicted_label": result,
                            "deployment_id": self.deployment_id,
                            "stage": self.stage
                        }
                    else:
                        return {"error": "Model class must have a 'classify_text' method"}
                        
                except Exception as e:
                    return {"error": f"Prediction failed: {str(e)}"}
        
        # Deploy the model
        ModelDeployment.deploy()
        
        print(f"Model deployed successfully!")
        print(f"Deployment ID: {self.deployment_id}")
        print(f"Stage: {self.stage}")
        print(f"Endpoint: http://localhost:8000/{self.deployment_name}")
        print(f"Example: curl 'http://localhost:8000/{self.deployment_name}?text=Great%20service!'")
        
        return {
            "deployment_id": self.deployment_id,
            "deployment_name": self.deployment_name,
            "endpoint": f"http://localhost:8000/{self.deployment_name}",
            "stage": self.stage
        }
