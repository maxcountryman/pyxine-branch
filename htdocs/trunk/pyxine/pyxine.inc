<?php // -*-php-*-
include('template.inc');

class Page extends Template
{
  function Page($page_title) {
    $this->Template('pyxine.tmpl');
    $this->set('TITLE', $page_title);
    $idx = new Template('index.tmpl');
    $idx->set('SELECTED', $page_title);
    $this->set_raw('INDEX', $idx->as_html());
    ob_start();
  }

  function flush() {
    $this->set_raw('BODY', ob_get_contents());
    ob_end_clean();
    $this->print_html();
  }
}

function docutils_output($filename)
{
  $fp = fopen($filename, "r");

  while ($line = fgets($fp, 2048)) {
    if ($line == "<body>\n")
      break;
  }

  while ($line = fgets($fp, 2048)) {
    if ($line == "</body>\n")
      break;

    /*
    $line = str_replace('<div class="contents topic" id="table-of-contents">',
                        '<div class="contents topic">',
                        $line);

    $line = str_replace('<a name="table-of-contents">',
                        '<a id="table-of-contents">',
                        $line);
    */
    print $line;
  }

  fclose ($fp);
}

?>
