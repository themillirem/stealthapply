"""
Job listing management for StealthApply.
Provides a static list of SolidWorks engineering roles in Minneapolis-St. Paul
plus hooks for future live scraping.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobListing:
    """Represents a single job listing."""
    company: str
    title: str
    location: str
    url: str
    description: str = ""
    job_id: str = ""

    def display_name(self) -> str:
        """Return a formatted display string for the UI."""
        return f"{self.company}  —  {self.title}"

    def full_description(self) -> str:
        """Return the full description for LLM context."""
        return (
            f"Company: {self.company}\n"
            f"Title: {self.title}\n"
            f"Location: {self.location}\n"
            f"Description: {self.description or 'SolidWorks engineering role'}\n"
        )


# Static job listings: 15+ SolidWorks engineering roles in Minneapolis-St. Paul
STATIC_JOBS: list[JobListing] = [
    JobListing(
        company="Medtronic",
        title="Mechanical Design Engineer",
        location="Fridley, MN",
        url="https://jobs.medtronic.com",
        description="Design and develop medical devices using SolidWorks. Collaborate with cross-functional teams on implantable cardiac products.",
    ),
    JobListing(
        company="Boston Scientific",
        title="Product Development Engineer",
        location="Maple Grove, MN",
        url="https://jobs.bostonscientific.com",
        description="SolidWorks-based product development for minimally invasive medical devices. GD&T, tolerance analysis, and DFM required.",
    ),
    JobListing(
        company="Graco Inc.",
        title="Senior Mechanical Engineer",
        location="Minneapolis, MN",
        url="https://graco.com/careers",
        description="Lead mechanical design of fluid handling equipment. SolidWorks, FEA, and hydraulic systems experience preferred.",
    ),
    JobListing(
        company="The Toro Company",
        title="Design Engineer",
        location="Bloomington, MN",
        url="https://thetorocompany.com/careers",
        description="Develop outdoor power equipment using SolidWorks. Experience with sheet metal, castings, and injection molded plastics.",
    ),
    JobListing(
        company="Polaris Industries",
        title="Mechanical Engineer",
        location="Medina, MN",
        url="https://polaris.com/careers",
        description="Design powersports vehicle components using SolidWorks. Strong understanding of manufacturing processes and cost drivers.",
    ),
    JobListing(
        company="3M",
        title="Research & Development Engineer",
        location="Maplewood, MN",
        url="https://3m.com/careers",
        description="R&D engineer supporting new product introduction. SolidWorks and rapid prototyping experience required.",
    ),
    JobListing(
        company="Eaton Corporation",
        title="Product Design Engineer",
        location="Eden Prairie, MN",
        url="https://eaton.com/careers",
        description="Design electrical and hydraulic components using SolidWorks. Experience with DFMEA and product lifecycle management.",
    ),
    JobListing(
        company="Donaldson Company",
        title="Mechanical Design Engineer",
        location="Minneapolis, MN",
        url="https://donaldson.com/careers",
        description="Filtration system design using SolidWorks. CFD knowledge and experience with industrial filtration a plus.",
    ),
    JobListing(
        company="Watlow Electric",
        title="Application Engineer",
        location="Winona, MN",
        url="https://watlow.com/careers",
        description="Thermal system design and customer-facing application engineering. SolidWorks for custom heater designs.",
    ),
    JobListing(
        company="Innovex",
        title="Senior Design Engineer",
        location="Bloomington, MN",
        url="https://innovex.com/careers",
        description="Medical device design using SolidWorks. Class II/III device experience and ISO 13485 knowledge preferred.",
    ),
    JobListing(
        company="Textron Arctic Cat",
        title="Product Engineer",
        location="Thief River Falls, MN",
        url="https://textron.com/careers",
        description="Snowmobile and ATV product engineering using SolidWorks. Hands-on testing and validation experience required.",
    ),
    JobListing(
        company="Taylor Made Solutions",
        title="Mechanical Engineer",
        location="Burnsville, MN",
        url="https://taylormade.com/careers",
        description="Custom manufacturing solutions engineering. SolidWorks, sheet metal, and weldment design.",
    ),
    JobListing(
        company="IDEX Corporation",
        title="Design Engineer",
        location="Bloomington, MN",
        url="https://idexcorp.com/careers",
        description="Pump and flow measurement product design using SolidWorks. Fluid dynamics and precision machining knowledge.",
    ),
    JobListing(
        company="Roper Technologies",
        title="Mechanical Design Engineer",
        location="Minneapolis, MN",
        url="https://ropertech.com/careers",
        description="Industrial instrumentation design with SolidWorks. Experience with sensors, transducers, and precision assemblies.",
    ),
    JobListing(
        company="Colder Products Company",
        title="Application Engineer",
        location="St. Paul, MN",
        url="https://colder.com/careers",
        description="Quick-disconnect coupling design and application support using SolidWorks. Customer-facing role with design responsibilities.",
    ),
    JobListing(
        company="Strattec Security",
        title="Mechanical Engineer",
        location="Plymouth, MN",
        url="https://strattec.com/careers",
        description="Automotive security component design using SolidWorks. Injection molded plastics and die casting experience preferred.",
    ),
    JobListing(
        company="API Technologies",
        title="Mechanical Design Engineer",
        location="Eden Prairie, MN",
        url="https://apitech.com/careers",
        description="Defense and aerospace component design using SolidWorks. Security clearance a plus.",
    ),
]


def get_all_jobs() -> list[JobListing]:
    """Return all available job listings."""
    return STATIC_JOBS.copy()


def get_jobs_by_company(company: str) -> list[JobListing]:
    """Return job listings filtered by company name (case-insensitive)."""
    return [j for j in STATIC_JOBS if company.lower() in j.company.lower()]
