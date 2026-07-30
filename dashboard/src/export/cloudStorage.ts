export interface CloudUploadConfig {
  provider: 's3' | 'gcs' | 'azure';
  bucket: string;
  path: string;
  file: Blob;
  metadata?: Record<string, string>;
  onProgress?: (progress: number) => void;
}

async function getPresignedUrl(provider: string, bucket: string, path: string): Promise<{
  url: string;
  fields?: Record<string, string>;
}> {
  const response = await fetch('/api/v1/storage/presign', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, bucket, path }),
  });
  return response.json();
}

export async function uploadToCloud(config: CloudUploadConfig): Promise<string> {
  const { url } = await getPresignedUrl(config.provider, config.bucket, config.path);
  
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && config.onProgress) {
        config.onProgress(e.loaded / e.total);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(`https://${config.bucket}.s3.amazonaws.com/${config.path}`);
      } else {
        reject(new Error(`Upload failed: ${xhr.statusText}`));
      }
    });
    
    xhr.addEventListener('error', () => reject(new Error('Upload failed')));
    
    xhr.open('PUT', url);
    if (config.metadata) {
      Object.entries(config.metadata).forEach(([k, v]) => {
        xhr.setRequestHeader(`x-amz-meta-${k}`, v);
      });
    }
    xhr.send(config.file);
  });
}
