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

?>
