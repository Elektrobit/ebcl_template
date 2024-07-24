Get ubuntu.tar:
```bash
docker run -d --name ubuntu ubuntu
docker export ubuntu > ubuntu.tar
```

Build image:
```bash
embdgen -o image.raw raspberry-pi-image.yaml
```
