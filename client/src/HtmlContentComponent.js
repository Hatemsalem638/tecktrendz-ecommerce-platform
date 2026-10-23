import React from 'react';

function HtmlContentComponent() {
  const rawHtml = "<p>Hello, <strong>world!</strong></p>";

  return (
    <div dangerouslySetInnerHTML={{ __html: rawHtml }} />
  );
}

export default HtmlContentComponent;
