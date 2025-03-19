const ImageViewer = ({ images }) => {
  return (
    <div className="image-gallery">
      {images.map((img, index) => (
        <div key={index}>
          {img.startsWith('data:image') ? (
            <img src={img} alt={`result-${index}`} />
          ) : (
            <a href={`${img}`} download>
              <img src={`${img}`} alt={`result-${index}`} />
              <button>下载</button>
            </a>
          )}
        </div>
      ))}
    </div>
  );
};

export default ImageViewer;