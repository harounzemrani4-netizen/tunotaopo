/**
 * QR en SVG, en el navegador. Byte mode, corrección M.
 * Sin llamadas externas. Suficiente para URLs de TuNotaOpo.
 */
(function (root) {
  "use strict";

  var EXP = new Array(512);
  var LOG = new Array(256);
  (function initGf() {
    var x = 1;
    var i;
    for (i = 0; i < 255; i += 1) {
      EXP[i] = x;
      LOG[x] = i;
      x <<= 1;
      if (x & 256) x ^= 285;
    }
    for (i = 255; i < 512; i += 1) EXP[i] = EXP[i - 255];
  })();

  function gfMul(a, b) {
    if (!a || !b) return 0;
    return EXP[LOG[a] + LOG[b]];
  }

  function rsGenerator(ecLen) {
    var poly = [1];
    var i;
    var j;
    for (i = 0; i < ecLen; i += 1) {
      var next = new Array(poly.length + 1);
      var k;
      for (k = 0; k < next.length; k += 1) next[k] = 0;
      for (j = 0; j < poly.length; j += 1) {
        next[j] ^= gfMul(poly[j], EXP[i]);
        next[j + 1] ^= poly[j];
      }
      poly = next;
    }
    return poly;
  }

  function rsEncode(data, ecLen) {
    var gen = rsGenerator(ecLen);
    var ecc = new Array(ecLen);
    var i;
    var j;
    for (i = 0; i < ecLen; i += 1) ecc[i] = 0;
    for (i = 0; i < data.length; i += 1) {
      var factor = data[i] ^ ecc[0];
      for (j = 0; j < ecLen - 1; j += 1) {
        ecc[j] = ecc[j + 1] ^ gfMul(gen[j + 1], factor);
      }
      ecc[ecLen - 1] = gfMul(gen[ecLen], factor);
    }
    return ecc;
  }

  /* version -> [totalCodewords, ecPerBlock, blocks] ECC M */
  var VERSIONS = {
    2: [44, 16, 1],
    3: [70, 26, 1],
    4: [100, 18, 2],
    5: [134, 24, 2],
    6: [172, 16, 4],
    7: [196, 18, 4],
    8: [242, 22, 4],
    9: [292, 22, 5],
    10: [346, 26, 5],
    11: [404, 30, 5],
    12: [466, 22, 8],
    13: [532, 22, 9],
    14: [581, 24, 9]
  };

  var ALIGN = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66]
  };

  function bitBuffer() {
    var bits = [];
    return {
      push: function (value, len) {
        var i;
        for (i = len - 1; i >= 0; i -= 1) bits.push((value >>> i) & 1);
      },
      toBytes: function () {
        var bytes = [];
        var i;
        for (i = 0; i < bits.length; i += 8) {
          var b = 0;
          var j;
          for (j = 0; j < 8; j += 1) {
            b = (b << 1) | (bits[i + j] || 0);
          }
          bytes.push(b);
        }
        return bytes;
      },
      length: function () {
        return bits.length;
      }
    };
  }

  function chooseVersion(byteLen) {
    var v;
    for (v = 2; v <= 14; v += 1) {
      var spec = VERSIONS[v];
      var dataCw = spec[0] - spec[1] * spec[2];
      var cap = dataCw - 2;
      var charBits = v >= 10 ? 16 : 8;
      var need = 4 + charBits + byteLen * 8 + 4;
      if (Math.ceil(need / 8) <= dataCw) return v;
      if (cap >= byteLen + 3) return v;
    }
    throw new Error("El texto es demasiado largo para el QR.");
  }

  function encodeBytes(text, version) {
    var bytes = [];
    var i;
    for (i = 0; i < text.length; i += 1) {
      var code = text.charCodeAt(i);
      if (code > 255) {
        var encoded = unescape(encodeURIComponent(text));
        bytes = [];
        for (i = 0; i < encoded.length; i += 1) bytes.push(encoded.charCodeAt(i) & 255);
        break;
      }
      bytes.push(code);
    }
    if (!bytes.length && text.length) {
      var utf = unescape(encodeURIComponent(text));
      for (i = 0; i < utf.length; i += 1) bytes.push(utf.charCodeAt(i) & 255);
    }
    var spec = VERSIONS[version];
    var dataCw = spec[0] - spec[1] * spec[2];
    var buf = bitBuffer();
    buf.push(4, 4);
    buf.push(bytes.length, version >= 10 ? 16 : 8);
    for (i = 0; i < bytes.length; i += 1) buf.push(bytes[i], 8);
    var maxBits = dataCw * 8;
    var remain = maxBits - buf.length();
    if (remain > 4) buf.push(0, 4);
    else if (remain > 0) buf.push(0, remain);
    while (buf.length() % 8) buf.push(0, 1);
    var data = buf.toBytes();
    var pad = 0;
    while (data.length < dataCw) {
      data.push(pad % 2 === 0 ? 236 : 17);
      pad += 1;
    }
    data = data.slice(0, dataCw);
    var blocks = spec[2];
    var ecLen = spec[1];
    var shortBlocks = blocks - (dataCw % blocks);
    var shortLen = Math.floor(dataCw / blocks);
    var groups = [];
    var offset = 0;
    for (i = 0; i < blocks; i += 1) {
      var len = shortLen + (i < shortBlocks ? 0 : 1);
      var block = data.slice(offset, offset + len);
      offset += len;
      groups.push({ data: block, ecc: rsEncode(block, ecLen) });
    }
    var interleaved = [];
    var maxData = shortLen + 1;
    var r;
    var b;
    for (r = 0; r < maxData; r += 1) {
      for (b = 0; b < groups.length; b += 1) {
        if (r < groups[b].data.length) interleaved.push(groups[b].data[r]);
      }
    }
    for (r = 0; r < ecLen; r += 1) {
      for (b = 0; b < groups.length; b += 1) interleaved.push(groups[b].ecc[r]);
    }
    return interleaved;
  }

  function sizeOf(version) {
    return version * 4 + 17;
  }

  function inFinder(x, y, size) {
    var boxes = [
      [0, 0],
      [size - 7, 0],
      [0, size - 7]
    ];
    var i;
    for (i = 0; i < boxes.length; i += 1) {
      var dx = x - boxes[i][0];
      var dy = y - boxes[i][1];
      if (dx >= 0 && dx <= 6 && dy >= 0 && dy <= 6) return true;
    }
    return false;
  }

  function finderModule(x, y, size) {
    var boxes = [
      [0, 0],
      [size - 7, 0],
      [0, size - 7]
    ];
    var i;
    for (i = 0; i < boxes.length; i += 1) {
      var dx = x - boxes[i][0];
      var dy = y - boxes[i][1];
      if (dx >= 0 && dx <= 6 && dy >= 0 && dy <= 6) {
        return dx === 0 || dx === 6 || dy === 0 || dy === 6 || (dx >= 2 && dx <= 4 && dy >= 2 && dy <= 4);
      }
    }
    return false;
  }

  function inAlign(x, y, version, size) {
    var pos = ALIGN[version] || [];
    var i;
    var j;
    for (i = 0; i < pos.length; i += 1) {
      for (j = 0; j < pos.length; j += 1) {
        var ax = pos[i];
        var ay = pos[j];
        if ((ax === 6 && ay === 6) || (ax === 6 && ay === size - 7) || (ax === size - 7 && ay === 6)) continue;
        if (Math.abs(x - ax) <= 2 && Math.abs(y - ay) <= 2) return true;
      }
    }
    return false;
  }

  function alignModule(x, y, version, size) {
    var pos = ALIGN[version] || [];
    var i;
    var j;
    for (i = 0; i < pos.length; i += 1) {
      for (j = 0; j < pos.length; j += 1) {
        var ax = pos[i];
        var ay = pos[j];
        if ((ax === 6 && ay === 6) || (ax === 6 && ay === size - 7) || (ax === size - 7 && ay === 6)) continue;
        var dx = Math.abs(x - ax);
        var dy = Math.abs(y - ay);
        if (dx <= 2 && dy <= 2) return dx === 2 || dy === 2 || (dx === 0 && dy === 0);
      }
    }
    return false;
  }

  function isReserved(x, y, version, size) {
    if (inFinder(x, y, size)) return true;
    if (x === 6 || y === 6) return true;
    if (inAlign(x, y, version, size)) return true;
    if (y === 8 && (x <= 8 || x >= size - 8)) return true;
    if (x === 8 && (y <= 8 || y >= size - 8)) return true;
    if (version >= 7) {
      if (x < 6 && y >= size - 11) return true;
      if (y < 6 && x >= size - 11) return true;
    }
    return false;
  }

  function maskBit(mask, x, y) {
    if (mask === 0) return (x + y) % 2 === 0;
    if (mask === 1) return y % 2 === 0;
    if (mask === 2) return x % 3 === 0;
    if (mask === 3) return (x + y) % 3 === 0;
    if (mask === 4) return (Math.floor(y / 2) + Math.floor(x / 3)) % 2 === 0;
    if (mask === 5) return ((x * y) % 2) + ((x * y) % 3) === 0;
    if (mask === 6) return (((x * y) % 2) + ((x * y) % 3)) % 2 === 0;
    return (((x + y) % 2) + ((x * y) % 3)) % 2 === 0;
  }

  function placeFormat(grid, size, mask) {
    var data = (0x03 << 13) | (mask << 10);
    var bch = data;
    var i;
    for (i = 0; i < 15; i += 1) {
      if (bch & 0x4000) bch = (bch << 1) ^ 0x537;
      else bch <<= 1;
    }
    var bits = (data | (bch & 0x3ff)) ^ 0x5412;
    var coords = [
      [0, 8], [1, 8], [2, 8], [3, 8], [4, 8], [5, 8], [7, 8], [8, 8],
      [8, 7], [8, 5], [8, 4], [8, 3], [8, 2], [8, 1], [8, 0]
    ];
    var coords2 = [
      [8, size - 1], [8, size - 2], [8, size - 3], [8, size - 4], [8, size - 5], [8, size - 6], [8, size - 7],
      [size - 8, 8], [size - 7, 8], [size - 6, 8], [size - 5, 8], [size - 4, 8], [size - 3, 8], [size - 2, 8], [size - 1, 8]
    ];
    for (i = 0; i < 15; i += 1) {
      var bit = (bits >> i) & 1;
      grid[coords[i][1]][coords[i][0]] = bit;
      grid[coords2[i][1]][coords2[i][0]] = bit;
    }
    grid[size - 8][8] = 1;
  }

  function buildGrid(version, codewords, mask) {
    var size = sizeOf(version);
    var grid = [];
    var reserved = [];
    var y;
    var x;
    for (y = 0; y < size; y += 1) {
      grid[y] = [];
      reserved[y] = [];
      for (x = 0; x < size; x += 1) {
        grid[y][x] = 0;
        reserved[y][x] = isReserved(x, y, version, size);
      }
    }
    for (y = 0; y < size; y += 1) {
      for (x = 0; x < size; x += 1) {
        if (inFinder(x, y, size)) grid[y][x] = finderModule(x, y, size) ? 1 : 0;
        else if (x === 6 || y === 6) grid[y][x] = (x + y) % 2 === 0 ? 1 : 0;
        else if (inAlign(x, y, version, size)) grid[y][x] = alignModule(x, y, version, size) ? 1 : 0;
      }
    }
    var bitStr = [];
    var i;
    var b;
    for (i = 0; i < codewords.length; i += 1) {
      for (b = 7; b >= 0; b -= 1) bitStr.push((codewords[i] >> b) & 1);
    }
    var idx = 0;
    var col;
    var upward = true;
    for (col = size - 1; col > 0; col -= 2) {
      if (col === 6) col = 5;
      var row;
      for (row = 0; row < size; row += 1) {
        y = upward ? size - 1 - row : row;
        for (i = 0; i < 2; i += 1) {
          x = col - i;
          if (!reserved[y][x] && idx < bitStr.length) {
            var bit = bitStr[idx];
            idx += 1;
            if (maskBit(mask, x, y)) bit ^= 1;
            grid[y][x] = bit;
          }
        }
      }
      upward = !upward;
    }
    placeFormat(grid, size, mask);
    return grid;
  }

  function toSvg(text) {
    var value = String(text || "");
    if (!value) throw new Error("No hay texto para el QR.");
    var version = chooseVersion(unescape(encodeURIComponent(value)).length);
    var codewords = encodeBytes(value, version);
    var grid = buildGrid(version, codewords, 0);
    var size = grid.length;
    var quiet = 2;
    var dim = size + quiet * 2;
    var parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + dim + " " + dim + '" width="180" height="180" role="img" aria-label="Código QR">'];
    parts.push('<rect width="' + dim + '" height="' + dim + '" fill="#fff"/>');
    var y;
    var x;
    for (y = 0; y < size; y += 1) {
      for (x = 0; x < size; x += 1) {
        if (grid[y][x]) {
          parts.push('<rect x="' + (x + quiet) + '" y="' + (y + quiet) + '" width="1" height="1" fill="#0c1924"/>');
        }
      }
    }
    parts.push("</svg>");
    return parts.join("");
  }

  root.NotaOpoQR = { toSvg: toSvg };
})(typeof window !== "undefined" ? window : globalThis);
