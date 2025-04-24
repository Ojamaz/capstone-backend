// small util to draw a filled hexagon
export default function drawHex(ctx, { x, y }, size, fill, glow) {
    ctx.save();
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      ctx.lineTo(
        x + size * Math.cos((Math.PI / 3) * i),
        y + size * Math.sin((Math.PI / 3) * i)
      );
    }
    ctx.closePath();
    if (glow) {
      ctx.shadowBlur = 15;
      ctx.shadowColor = glow;
    }
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.restore();
  }
  