import './globals.css'

export const metadata = {
  title: 'Soundscapes',
  description: 'Spotify IRL',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
