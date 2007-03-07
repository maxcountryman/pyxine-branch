<?php // -*-php-*-

class Template {
  function Template($file) {
    $this->_file = $file;
    $this->_vars = array();
  }

  function set($name, $value) {
    $this->_vars[$name] = $this->_quote($value);
  }

  function set_raw($name, $value) {
    $this->_vars[$name] = $value;
  }

  function print_html() {
    extract($this->_vars);
    include($this->_file);
  }

  function as_html() {
    ob_start();
    $this->print_html();
    $html = ob_get_contents();
    ob_end_clean();
    return $html;
  }

  function _quote($val) {
    if (is_array($val))
      return $this->_quote_array($val);
    else
      return htmlspecialchars($val);
  }

  function _quote_array($val) {
    $quoted = array();
    foreach ($val as $key => $val) {
      $quoted[htmlspecialchars($val)] = $this->_quote($val);
    }
    return $quoted;
  }
}

?>
